import argparse
import networkx as nx
import os
from .utils import log
from .graph_builder import GraphBuilder
from .graph_utils import GraphUtils

parser = argparse.ArgumentParser(description='Runs graph building pipeline.')
parser.add_argument('-t', '--test', action='store_const',
                    const=True, default=False,
                    help='runs the pipeline on test data')

args = parser.parse_args()

if args.test:
    log("-t: Running the pipeline on test data")
    json_path = os.path.dirname(os.path.abspath(__file__)) \
                + "\\test_users_master.json"
    graph_path = os.path.dirname(os.path.abspath(__file__)) \
                 + "\\test_master_graph.gml"
else:
    json_path = os.path.dirname(os.path.abspath(__file__)) \
                + "\\wip_data\\users_master.json"
    graph_path = os.path.dirname(os.path.abspath(__file__)) \
                 + "\\wip_data\\master_graph.gml"

gb = GraphBuilder(json_master_path=json_path)
kwargs = {'trim_min_users': 50,
          'trim_optimal_users': 80,
          'trim_optimal_number_of_games_per_user': 40}
G = gb.get_graph(
    std_coefficient=7,
    min_neighbours=3,
    **kwargs)
log('Graph created')

nx.write_gml(G, graph_path)
log('Graph saved to:' + graph_path)

gu = GraphUtils(
        graph_path=graph_path,
        users_master_json_path=json_path)
gu.set_node_sizes()
gu.set_node_colors(method='tsne_3d')
gu.set_node_names()
gu.write_graph()

log('Graph: added sizes, colors, names')
