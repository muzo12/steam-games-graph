import math
import json
import requests
import networkx as nx
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scripts import log, Encoder

class GraphUtils:
    """This class holds all utils to work with graphs:

    1. Colorize nodes
    2. Change nodes size
    3. Change nodes names"""

    def __init__(self,
                 graph_path="wip_data/master_graph.gml",
                 users_master_json_path="wip_data/users_master.json"):
        self.graph_path = graph_path
        self.graph = self.read_graph()
        self.users_master_json_path = users_master_json_path

        self.raw_weights = None

    def read_graph(self) -> nx.Graph:
        """Reads graph to disc and returns it."""
        G = nx.read_gml(self.graph_path)
        log("Graph loaded successfully")
        return G

    def write_graph(self):
        """Writes graph back to disc."""
        nx.write_gml(self.graph, self.graph_path)
        log("Graph written successfully")

    def set_node_sizes(
            self,
            min_value = 10,
            max_value = 100,
            func = lambda x: (math.log(x + 1, 5) + 1) ** 2):
        """Calculates node sizes.

        :param func: Function to perform on node's weight.
            (Weight is number of game owners.)
        """

        def get_raw_weights():
            """Reads users_master.json file and returns weights of all games
            (number of users who have the game.)"""

            if self.raw_weights is not None:
                return self.raw_weights

            with open(self.users_master_json_path) as f:
                json_users = json.load(f)

            encoder = Encoder()

            games_raw_weights = {}

            for user, i in zip(json_users, range(len(json_users))):

                if i % 10000 == 0:
                    log('Progress: {}/{} ({:.3f}%)'.format(
                        i, len(json_users), i / len(json_users) * 100))

                try:
                    games_alpha = user['g']
                except KeyError:
                    continue

                try:
                    games_arr = encoder.decode_games_string(games_alpha)
                except AssertionError:
                    continue

                for game in games_arr:
                    try:
                        games_raw_weights[game] += 1
                    except KeyError:
                        games_raw_weights[game] = 1

                # if i > 50000:
                #     break

            self.raw_weights = games_raw_weights

            return games_raw_weights

        def normalize(
                sizes: dict,
                min_val: float = None,
                max_val: float = None) -> dict:

            if min_val is None or max_val is None:
                log("Sizes not normalized")
                return sizes

            keys = list(sizes.keys())
            values = list(sizes.values())
            sizes_min = np.min(values)
            sizes_max = np.max(values)
            values_scaled = [min_val +
                             (x - sizes_min) * (max_val - min_val)/
                             (sizes_max - sizes_min) for x in values]
            return dict(zip(keys, values_scaled))

        log("Calculating games weights...")

        sizes = {}
        for key, value in get_raw_weights().items():
            sizes[key] = func(value)

        graph_node_sizes = {}
        for node in self.graph.nodes():
            try:
                # log(node, sizes[node])
                graph_node_sizes[node] = sizes[int(node)]
            except KeyError:
                log("Node {} not found in users_master.json file!"
                    .format(node))
                graph_node_sizes[node] = 1

        sizes_normalized = normalize(
            graph_node_sizes,
            min_value,
            max_value)

        nx.set_node_attributes(self.graph, sizes_normalized, 'size')

        log("Calculating games weights... Complete")

    def set_node_names(self):
        """Queries Steam's API to gather names for games present in the graph.
        """

        # TODO offline json backup

        log("Querying Steam to get app names...")

        request = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        try:
            response = requests.get(request)
        except TimeoutError:
            log('Steam API: timeout error')
            return

        try:
            json_response = json.loads(response.text)
        except:
            log("Steam API: wrong response")
            return

        apps = {}
        for app in json_response['applist']['apps']:
            try:
                apps[int(app['appid'])] = app['name']
            except KeyError:
                log("error with app: {}".format(app))

        names_dict = {}
        for node in self.graph.nodes():
            try:
                name = apps[int(node)]
            except KeyError:
                log("name not found for game: {}".format(node))
                name = str(node)
            names_dict[node] = name

        nx.set_node_attributes(self.graph, names_dict, 'name')

        log("Querying Steam to get app names... Complete")

    def set_node_colors(self,
                 method='tsne_3d'):
        """Colorizes graph based on given method, and stores result in
        given label within the graph.

        :param method:
        :return:
        """

        log("Colorizing game nodes...")

        def normalize_to_color_space(
                pos: np.ndarray,
                min_val=0.25,
                max_val=0.9,
                loss = 0.1) -> np.ndarray:

            """Returns copy of position array normalized to be used as color.

            This algorithm is dumb, but calculations are cheap,
            so we can afford it!

            :param pos: position np.ndarray
            :param min_val: expected minimum value
            :param max_val: expected maximum value
            :param loss: expected loss of transformation - ratio of values
                clipped to lower or upper bound.
                Lower loss -> less clipping, values more pushed together
                Higher loss -> more clipping, values less pushed together
            :return: normalized position np.ndarray
            """

            def _normalize_pass(std_factor) -> tuple:
                """Returns (normalized positions, loss) tuple."""

                norm = pos.copy()

                norm_mean = np.mean(norm, axis=0)
                norm_std = np.std(norm, axis=0)

                norm -= norm_mean
                norm /= norm_std * std_factor

                norm -= -1
                norm *= (max_val - min_val)
                norm /= 2
                norm += min_val

                min_mask = norm < min_val
                min_mask_inv = np.ones(min_mask.shape) - min_mask
                norm *= min_mask_inv
                norm += min_mask * min_val

                max_mask = norm > max_val
                max_mask_inv = np.ones(max_mask.shape) - max_mask
                norm *= max_mask_inv
                norm += max_mask * max_val

                clipped_total = np.sum(min_mask) + np.sum(max_mask)
                loss = clipped_total / (pos.shape[0] * pos.shape[1])

                return norm, loss

            results = []
            for i in np.arange(0.1, 2, 0.025):
                results.append(_normalize_pass(i))

            best_result, best_loss = results[0]
            for res, ls in results:
                if abs(loss - ls) < abs(loss - best_loss):
                    best_result = res
                    best_loss = ls

            log('best loss:', best_loss)
            log('best result: mean: {:.3f} std: {:.3f}'.
                format(np.mean(best_result), np.std(best_result)))

            return best_result

        mtx = nx.to_numpy_matrix(self.graph)
        embedding = None

        if method == 'tsne_3d':
            tsne = TSNE(n_components=3, verbose=True)
            embedding = tsne.fit_transform(mtx)

        elif method == 'pca_3d':
            pca = PCA(n_components=3)
            embedding = pca.fit_transform(mtx)

        if embedding is not None:
            normalized = normalize_to_color_space(embedding)
            hex_values = self._to_hex(normalized)
            hex_values_dict = dict(zip(list(self.graph.nodes()), hex_values))

            nx.set_node_attributes(self.graph, hex_values_dict, 'color')

        log("Colorizing game nodes... Complete")

    @staticmethod
    def _to_hex(ndarray) -> list:
        results = []
        for arr in ndarray:
            assert min(arr) >= 0
            assert max(arr) <= 1
            arr_256 = (np.asarray(arr) * 256).astype(np.int32)
            result = ''
            for i in arr_256:
                result += "{:02x}".format(i)
            results.append(result)
        return results


if __name__ == '__main__':
    gu = GraphUtils(
        graph_path="test_master_graph.gml",
        users_master_json_path="test_users_master.json")
    gu.set_node_sizes()
    gu.set_node_colors(method='tsne_3d')
    gu.set_node_names()
    gu.write_graph()
