import numpy as np
import networkx as nx
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scripts import log


class GraphUtilsNodeColor:
    """This class holds all utils necessary to colorize master graph nodes."""

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

    def colorize(self,
                 method='tsne_3d',
                 save_label='color'):
        """Colorizes graph based on given method, and stores result in
        given label within the graph.
        
        :param method:
        :param save_label: 
        :return: 
        """

        log("Colorizing game nodes...")

        def normalize_to_color_space(
                pos,
                min_val=0.25,
                max_val=0.9,
                std_range=1.25) -> np.ndarray:

            """Returns copy of position array normalized to be used as color.

            :param pos: position np.ndarray
            :param min_val: expected minimum value
            :param max_val: expected maximum value
            :param std_range: range of transformation.
                Higher range -> less clipping, values more pushed together
                Lower range -> more clipping, values less pushed together
            :return: normalized position np.ndarray
            """
            norm = pos.copy()

            norm_mean = np.mean(norm, axis=0)
            norm_std = np.std(norm, axis=0)

            norm -= norm_mean
            norm /= norm_std * std_range

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
            log("Clipped {} values ({:.3f}%)".format(
                clipped_total,
                clipped_total / (pos.shape[0] * pos.shape[1]) * 100))

            norm_mean = np.mean(norm, axis=0)
            norm_std = np.std(norm, axis=0)

            log("After normalization: mean: {}, std: {}".format(
                norm_mean, norm_std))

            return norm

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
            nx.set_node_attributes(self.graph, save_label, hex_values_dict)

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
    gunc = GraphUtilsNodeColor()
    gunc.colorize(method='tsne_3d')
    gunc.write_graph()
