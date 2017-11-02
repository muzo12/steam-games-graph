import os
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import pairwise_distances
from scripts import Encoder, log


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
        self.filtered_matrix = None
        self.graph = None
        self.trimmed_games_dict = None
        self.indices = None

    def get_adjacency_matrix(
            self,
            **kwargs
    ) -> tuple:
        """Reads master json file and returns an adjacency matrix between games.        
        
        :return: (adjacency_matrix, indices): adjacency matrix between games
            and a list of corresponding game IDs.
        """

        if self.matrix is not None:
            return self.matrix, self.indices

        with open(self.json_master_path) as f:
            json_users = json.load(f)

        users_dict, games_dict = self._build_dicts(json_users)
        trimmed_games_dict = self._trim_games_dict(
            users_dict, games_dict, **kwargs)

        # to be used later for plots
        self.trimmed_games_dict = trimmed_games_dict

        ndarray, indices = self._build_bool_ndarray(trimmed_games_dict)

        distance_matrix = pairwise_distances(ndarray, metric='cosine')
        adjacency_matrix = np.ones(distance_matrix.shape) - distance_matrix

        self.matrix = adjacency_matrix
        self.indices = indices

        return adjacency_matrix, indices

    def get_filtered_adjacency_matrix(
            self,
            std_coefficient=4.5,
            min_neighbours=5,
            **kwargs
    ) -> tuple:
        """Returns a filtered adjacency matrix - i.e. one that discards
        low adjacency values (replaces them with 0s).
        
        For each game, filter threshold is calculated as:
            MEAN + std_coefficient * STANDARD_DEVIATION
        
        :param std_coefficient: standard deviation coefficient in filter
            threshold calculation.
        :type std_coefficient: float
        :param min_neighbours: minimal number of neighbours a game should have.
        :type min_neighbours: int
        :return: (adjacency_matrix, indices): filtered adjacency matrix 
            between games and list of corresponding game IDs.
        """

        if self.filtered_matrix is not None and self.indices is not None:
            return self.filtered_matrix, self.indices

        if self.matrix is not None and self.indices is not None:
            mtx = self.matrix
            indices = self.indices
        else:
            mtx, indices = self.get_adjacency_matrix(**kwargs)

        # discard self-adjacency for better mean and std calculation
        mtx *= (np.ones(mtx.shape) - np.identity(mtx.shape[0]))

        mean = np.mean(mtx, axis=1).reshape((mtx.shape[0], -1))
        std = np.std(mtx, axis=1).reshape((mtx.shape[0], -1))

        mask = mean + std_coefficient * std
        mask_mtx = (mtx > mask)

        # assure that at least min_neighbours are in mask
        sorted_mtx = np.sort(mtx, axis=1)
        idx = sorted_mtx.shape[1] - min(sorted_mtx.shape[1], min_neighbours)
        thresholds = sorted_mtx[:, idx].reshape(sorted_mtx.shape[0], -1)
        min_mask_mtx = mtx >= thresholds
        mask_mtx += min_mask_mtx

        masked_mtx = mask_mtx * mtx

        # add discarded self-adjacency back
        masked_mtx += np.identity(masked_mtx.shape[0])

        self.filtered_matrix = masked_mtx

        return masked_mtx, indices

    def get_graph(
            self,
            std_coefficient=4.5,
            min_neighbours=5,
            **kwargs
    ) -> nx.Graph:
        """Returns NetworkX graph of games.

        1. An adjacency matrix is calculated for all games.
        2. Adjacency matrix is filtered - low adjacency pairs are discarded.
        
        For each game, filter threshold is calculated as:
            MEAN + std_coefficient * STANDARD_DEVIATION
            
        3. A graph is constructed.

        :param std_coefficient: standard deviation coefficient in filter
            threshold calculation.
        :type std_coefficient: float
        :param min_neighbours: minimal number of neighbours a game should have.
        :type min_neighbours: int
        :return: NetworkX.Graph of games.
        """

        if self.graph is not None:
            return self.graph

        mtx, ind = self.get_filtered_adjacency_matrix(
            std_coefficient=std_coefficient,
            min_neighbours=min_neighbours,
            **kwargs)

        nonzero = np.count_nonzero(mtx, axis=1)
        log('non-zero elements in masked_adjacency matrix: '
            'median: {}, mean: {:.3f}, std: {:.3f}'.format(
             np.median(nonzero), np.mean(nonzero), np.std(nonzero)))

        graph = nx.from_numpy_matrix(mtx)
        mapping = dict(zip(graph.nodes(), ind))
        labeled_graph = nx.relabel_nodes(graph, mapping)

        log('Graph: # of nodes: {}, # of edges: {}'.format(
            len(labeled_graph.nodes()), len(labeled_graph.edges())))

        self.graph = labeled_graph

        return labeled_graph

    def plot_info(self):
        """To be called only after .get_graph(). 

        Plots graphs:

        1. Number of neighbours histogram
        2. Number of neighbours vs number of users
        """

        nonzeros = np.count_nonzero(self.filtered_matrix, axis=1)
        plt.subplot(211)
        plt.hist(nonzeros, bins=int(np.max(nonzeros) * 0.5))
        plt.title("Number of neighbours histogram")
        plt.xlabel("Number of neighbours")
        plt.ylabel("Occurence")
        plt.yscale("log", nonposy='clip')
        plt.grid(True)
        plt.text(30, 200,
                 r'$\mu={:.3f},\ \sigma={:.3f}$'.format(
                     np.mean(nonzeros), np.std(nonzeros)))

        plt.subplot(212)
        if self.trimmed_games_dict is not None and self.indices is not None:
            y = [len(self.trimmed_games_dict[x]) for x in self.indices]
            x = np.asarray(nonzeros).astype(np.float64)

            # add some randomness to x to make the scatter plot more legible
            d0 = np.asarray(x).shape[0]
            x += np.random.rand(d0, ) - np.ones(d0, ) * 0.5

            plt.xlabel("Number of neighbours")
            plt.ylabel("Number of users")
            plt.yscale("log", nonposy='clip')
            plt.grid(True)
            plt.scatter(x, y, alpha=0.3, s=7)

        plt.show()

    def _build_dicts(
            self,
            json_users: list
    ) -> tuple:
        """Given the json_master file, this method creates user:games 
        and game:users dicts for further transformation.

        :param json_users: List of users and their games (raw input).
        :return: (users_dict, games_dict) tuple.
        """

        users_dict = {}
        games_dict = {}

        for user, i in zip(json_users, range(len(json_users))):

            if i % 10000 == 0:
                log('progress: {}/{}: {:.3f}%'.format(i, len(json_users),
                                                      i/len(json_users)*100))
            i += 1

            try:
                user_games = self._get_games_array(user)
            except AssertionError:  # raised if user has no games
                continue

            user_name = self._get_user_name(user)
            users_dict[user_name] = user_games

            for game in user_games:
                try:
                    games_dict[game].add(user_name)
                except KeyError:
                    games_dict[game] = set(user_name)

            # if i > 5000:
            #     log('breaking building dicts after {} users'.format(i))
            #     break

        for game in games_dict.keys():
            games_dict[game] = list(games_dict[game])

        return users_dict, games_dict

    @staticmethod
    def _trim_games_dict(
            users_dict: dict,
            games_dict: dict,
            **kwargs
    ) -> dict:
        """Trims a games_dict to a minimal size.

        Given that the source games_dict might have hundreds of thousands
        of users, not all of these users give new meaningful
        information about relationships between games. Thus, this function
        aims to remove as many users as possible, but still leave enough
        so that every game could have a sizable and diverse users pool.

        :param users_dict: raw users_dict as created by _build_dicts()
        :type users_dict: dict
        :param games_dict: raw games_dict as created by _build_dicts()
        :type games_dict: dict
        :param min_users: minimal amount of users a game has to have in order
            not to be removed from pool of games.
        :type min_users: int
        :param optimal_users: minimal amount of users each game should have,
            if able.
        :type optimal_users: int
        :return: trimmed games_dict.
        """

        min_users = kwargs.pop('trim_min_users', 25)
        optimal_users = kwargs.pop('trim_optimal_users', 100)
        optimal_number_of_games = kwargs.pop(
            'trim_optimal_number_of_games_per_user', 20)

        def user_score(user_id, optimal_number=20):
            """Returns inverted distance from optimal_number_of_games.
            
            :param user_id: user id of queried user
            :type user_id: int
            :param optimal_number: number of games considered optimal
                for an user to have.
            :type optimal_number: int"""
            return 0 - abs(optimal_number - len(users_dict[user_id]))

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
            sorted_users = sorted(
                list(fresh_users),
                key=lambda user: user_score(user, optimal_number_of_games),
                reverse=True)
            saved_users |= set(sorted_users[:users_to_add])

            trimmed_games_dict[game] = list(set(game_users) & saved_users)

        log('_trim_games_dict: total users remaining:', len(saved_users))
        log('games remaining after trim:', len(trimmed_games_dict))

        return trimmed_games_dict

    @staticmethod
    def _build_bool_ndarray(games_dict: dict) -> tuple:
        """Given a games_dict, this method returns a corresponding games_dict,
        in which all values are lists of True/False values, depending on
        whether given user has the game.

        :param games_dict: Trimmed games_dict.
        :return: (dict, games_list) tuple.
        """
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
    def _get_games_array(user) -> list:

        try:
            games_str = user['g']
        except KeyError:
            raise AssertionError

        if games_str == "" or games_str == "error":
            raise AssertionError

        games_arr = Encoder(alphabet=Encoder.BASE11_ALPHABET
                            ).decode_user_games_alpha(games_str)
        return games_arr

    @staticmethod
    def _get_user_name(user) -> str:
        try:
            return user['p']
        except KeyError:
            return 'NoName'


if __name__ == '__main__':
    gb = GraphBuilder(json_master_path="/test_users_master.json")
    kwargs = {'trim_min_users': 25, 'trim_optimal_users': 150}
    gb.get_graph(**kwargs)
    gb.plot_info()
