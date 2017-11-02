import os
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import pairwise_distances
from scripts.encoder import Encoder


class GraphBuilder:
    """
    GraphBuilder gathers previously scrapped data from main json file,
    and returns a proximity matrix or networkx graph.

    1. Reads users_master.json users dict and creates corresponding games dict.
    2. Trims games dict to only have necessary users.
    3. For each game, creates an array which holds True or False values for
        each user, depending on whether they own the game.
    4. Considering this True/False array as a high-dimensional position vector,
        an adjacency matrix is created for all games.
    5. Optionally, a graph is created.
    """

    def __init__(self,
                 json_master_path="/wip_data/users_master.json"):
        self.json_master_path = os.path.dirname(__file__) + json_master_path
        self.matrix = None
        self.graph = None
        self.games_dict = None

    def get_adjacency_matrix(self) -> tuple:

        if self.matrix is not None:
            return self.matrix, self.indices

        with open(self.json_master_path) as f:
            json_users = json.load(f)

        users_dict, games_dict = self._build_dicts(json_users)

        print('users', len(users_dict))
        print('games', len(games_dict))

        trimmed_games_dict = self._trim_games_dict(users_dict, games_dict)

        # to be used later with plots
        self.games_dict = trimmed_games_dict

        print('games remaining after trim:', len(trimmed_games_dict))

        ndarray, indices = self._build_bool_ndarray(trimmed_games_dict)

        distance_matrix = pairwise_distances(ndarray, metric='cosine')
        adjacency_matrix = np.ones(distance_matrix.shape) - distance_matrix

        self.matrix = adjacency_matrix
        self.indices = indices

        return adjacency_matrix, indices

    def get_graph(self, threshold=4.5, min_neighbours=5):

        if self.graph is not None:
            return self.graph

        mtx, ind = self.get_adjacency_matrix()

        masked_adjacency = self._get_thresholded_adjacency_mtx(mtx, threshold, min_neighbours)

        print('non-zero elements in masked_adjacency matrix:')
        nonzero = np.count_nonzero(masked_adjacency, axis=1)
        print(nonzero)
        print('median: {}, mean: {}, std: {}'.format(
            np.median(nonzero), np.mean(nonzero), np.std(nonzero)))

        self._plot_info(masked_adjacency, indices=ind, games_dict=self.games_dict)

        G = nx.from_numpy_matrix(masked_adjacency)
        mapping = dict(zip(G.nodes, ind))
        H = nx.relabel_nodes(G, mapping)

        print('graph:')
        print('nodes: {}'.format(len(H.nodes)))
        # print(H.nodes)
        print('edges: {}'.format(len(H.edges)))
        # print(H.edges)

        self.graph = H

        return H

    def _build_dicts(self, json_users) -> tuple:
        """
        Given the json_master file, this method creates user:games and game:users
        dicts for further transformation.

        :param json_users:
        :return:
        """

        users_dict = {}
        games_dict = {}

        for user, i in zip(json_users, range(len(json_users))):
            user_name = self._get_user_name(user)
            try:
                user_games = self._get_games_array(user)
            except AssertionError:  # raised if user has no games
                continue

            users_dict[user_name] = user_games
            for game in user_games:
                try:
                    games_dict[game].append(user_name)
                except KeyError:
                    games_dict[game] = [user_name]

            if i % 1000 == 0:
                print('build_dict: i: ', i)
            i += 1

            # if i>5000:
            #     break

        return users_dict, games_dict

    @staticmethod
    def _trim_games_dict(users_dict, games_dict,
                         min_users=25, optimal_users=100) -> dict:
        """Trims a dataframe to a minimal size.

            Given that the source dataframe might be hundred thousands or even
            millions entries long, not all of these users give new meaningful
            information about relationships between games. Thus, this method
            aims to remove as much users as possible, but still leave enough
            so that every game could have a sizable and diverse users pool.

            Args:
                min_users (int) - minimal amount of users each game should
                    have, if able.
        """

        def user_score(user_id, optimal_number_of_games=20):
            """Returns inverted distance from optimal_number_of_games."""
            return 0 - abs(optimal_users-len(users_dict[user_id]))

        trimmed_games_dict = games_dict.copy()

        saved_users = set()

        games = games_dict.keys()
        for game in games:
            game_users = trimmed_games_dict[game]
            if len(game_users) < min_users:
                del trimmed_games_dict[game]
            elif len(game_users) < optimal_users:
                saved_users |= set(game_users)

        for game, game_users in trimmed_games_dict.items():

            if len(game_users) < optimal_users:
                continue

            fresh_users = set(game_users) - saved_users
            users_to_add = optimal_users - len(set(game_users) & saved_users)
            sorted_users = sorted(list(fresh_users),
                                  key=lambda user: user_score(user),
                                  reverse=True)
            saved_users |= set(sorted_users[:users_to_add])

            trimmed_games_dict[game] = list(set(game_users) & saved_users)

        print('_trim_games_dict: total users remaining:', len(saved_users))

        return trimmed_games_dict

    @staticmethod
    def _build_bool_ndarray(games_dict) -> tuple:

        users_set = set()
        for game_users in games_dict.values():
            users_set |= set(game_users)

        users_list = list(users_set)
        arrays = []
        games = []
        for game, game_users in games_dict.items():
            games.append(game)
            arr = np.isin(users_list, game_users)
            arrays.append(arr)

        return np.asarray(arrays), games

    @staticmethod
    def _get_thresholded_adjacency_mtx(mtx, threshold, min_neighbours) -> np.ndarray:

        # discard self-adjacency for better mean and std calculation
        mtx *= (np.ones(mtx.shape) - np.identity(mtx.shape[0]))

        mean = np.mean(mtx, axis=1).reshape((mtx.shape[0], -1))
        std = np.std(mtx, axis=1).reshape((mtx.shape[0], -1))

        mask = mean + threshold * std
        mask_mtx = (mtx > mask)

        #assure that at least min_neighbours are in mask
        sorted_mtx = np.sort(mtx, axis=1)
        idx = sorted_mtx.shape[1] - min(sorted_mtx.shape[1], min_neighbours)
        thresholds = sorted_mtx[:, idx].reshape(sorted_mtx.shape[0], -1)
        min_mask_mtx = mtx >= thresholds
        mask_mtx += min_mask_mtx

        masked_mtx = mask_mtx * mtx

        #add discarded self-adjacency back
        masked_mtx += np.identity(masked_mtx.shape[0])

        return masked_mtx

    @staticmethod
    def _plot_info(mtx, indices=None, games_dict=None):
        nonzeros = np.count_nonzero(mtx, axis=1)
        plt.subplot(211)
        plt.hist(nonzeros, bins=np.max(nonzeros))
        plt.title("Number of neighbours histogram")
        plt.xlabel("Number of neighbours")
        plt.ylabel("Occurence")
        plt.yscale("log", nonposy='clip')
        plt.grid(True)
        plt.text(30, 200,
                 r'$\mu={:3f},\ \sigma={:3f}$'.format(np.mean(nonzeros), np.std(nonzeros)))

        plt.subplot(212)
        if games_dict is not None and indices is not None:
            y = [len(games_dict[x]) for x in indices]
            x = np.asarray(nonzeros).astype(np.float64)

            # add little randomness to x to make scatterplot more legible
            d0 = np.asarray(x).shape[0]
            x += np.random.rand(d0, ) - np.ones(d0, ) * 0.5

            plt.xlabel("Number of neighbours")
            plt.ylabel("Number of users")
            plt.scatter(x, y, alpha=0.3, s=7)

        plt.show()

    @staticmethod
    def _get_games_array(user) -> list:

        try:
            games_str = user['g']
        except KeyError:
            # print('user jsonobject has no games key: ', user)
            raise AssertionError

        if games_str == "" or games_str == "error":
            raise AssertionError

        games_arr = Encoder(alphabet=Encoder.BASE11_ALPHABET).decode_user_games_alpha(games_str)
        return games_arr

    @staticmethod
    def _get_user_name(user) -> str:
        try:
            return user['p']
        except KeyError:
            return 'NoName'


if __name__ == '__main__':
    GraphBuilder(json_master_path="/test_users_master.json").get_graph()
