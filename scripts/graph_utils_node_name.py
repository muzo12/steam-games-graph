import json
import requests
import networkx as nx
from scripts import log

class GraphUtilsNodeName:

    def __init__(self,
                 graph_path="wip_data/master_graph.gml"):
        self.graph_path = graph_path
        self.graph = self.read_graph()

    def read_graph(self) -> nx.Graph:
        """Reads graph to disc and returns it."""
        G = nx.read_gml(self.graph_path)
        log("Graph loaded successfully")
        return G

    def write_graph(self):
        """Writes graph back to disc."""
        nx.write_gml(self.graph, self.graph_path)
        log("Graph written successfully")

    def get_names(self) -> list:
        """Queries Steam's API to gather names for games present in the graph.
        """

        log("Querying Steam to get app names...")

        request = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = requests.get(request)

        try:
            json_response = json.loads(response.text)
        except:
            log("Steam API: wrong response")
            return []

        apps = {}
        for app in json_response['applist']['apps']:
            try:
                apps[int(app['appid'])] = app['name']
            except KeyError:
                log("error with app: {}".format(app))

        names_dict = {}
        for node in self.graph.nodes():
            try:
                name = apps[node]
            except KeyError:
                log("name not found for game: {}".format(node))
                name = str(node)
            names_dict[node] = name

        nx.set_node_attributes(self.graph, 'name', names_dict)

        log("Querying Steam to get app names... Complete")

if __name__ == '__main__':
    gunn = GraphUtilsNodeName()
    gunn._get_names()
    gunn.write_graph()
