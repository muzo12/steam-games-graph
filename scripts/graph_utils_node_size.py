import math
import json
import networkx as nx
from scripts import log, Encoder

class GraphUtilsNodeSize:
    """This class holds all utils necessary to colorize master graph nodes."""

    def __init__(self,
                 graph_path="wip_data/master_graph.gml",
                 users_master_json_path="wip_data/users_master.json"):
        self.graph_path = graph_path
        self.graph = self.read_graph()
        self.users_master_json_path = users_master_json_path
        self.raw_weights_ = None
        self.encoder = Encoder(Encoder.BASE11_ALPHABET)

    def read_graph(self) -> nx.Graph:
        """Reads graph to disc and returns it."""
        G = nx.read_gml(self.graph_path)
        log("Graph loaded successfully")
        return G

    def write_graph(self):
        """Writes graph back to disc."""
        nx.write_gml(self.graph, self.graph_path)
        log("Graph written successfully")

    def _get_raw_weights(self):
        """Reads users_master.json file and returns weights of all games 
        (number of users who have the game.)"""

        if self.raw_weights_ is not None:
            return self.raw_weights_

        with open(self.users_master_json_path) as f:
            json_users = json.load(f)

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
                games_arr = self.encoder.decode_user_games_alpha(games_alpha)
            except AssertionError:
                continue

            for game in games_arr:
                try:
                    games_raw_weights[game] += 1
                except KeyError:
                    games_raw_weights[game] = 1

            # if i > 50000:
            #     break

        self.raw_weights_ = games_raw_weights

        return games_raw_weights

    def calculate_sizes(
            self,
            func=lambda x: (math.log(x + 1, 5) + 1) ** 2):
        """Calculates node sizes given a function to operate on nodes weights.
        """

        log("Calculating games weights...")

        sizes = {}
        for key, value in self._get_raw_weights().items():
            sizes[key] = func(value)

        graph_node_sizes = {}
        for node in self.graph.nodes():
            try:
                # log(node, sizes[node])
                graph_node_sizes[node] = sizes[node]
            except KeyError:
                log("Node {} not found in users_master.json file!"
                    .format(node))
                graph_node_sizes[node] = 1

        nx.set_node_attributes(self.graph, 'size', graph_node_sizes)

        log("Calculating games weights... Complete")

        return sizes

if __name__ == '__main__':
    guns = GraphUtilsNodeSize()
    guns.calculate_sizes()
    guns.write_graph()
