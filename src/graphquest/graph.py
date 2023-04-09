"""Functions for providing additional graph features on top of networkx."""
import math
import networkx as nx
import numpy as np
import random
from shapely import *

# Dimensions of the cartesian coordinate space that the nodes occupy
__WIDTH = 100
__HEIGHT = 100

# Minimum angle allowed between two edges (in radians)
__ANGLE_TOLERANCE = (15 / 180) * math.pi


def __random_positions(n: int):
    """Randomly chooses node positions within the coordinate space."""
    nodes = []

    def valid(u):
        for v in nodes:
            if math.dist(u, v) < math.sqrt(__WIDTH ** 2 + __HEIGHT ** 2) / n:
                return False
        return True

    while len(nodes) < n:
        m = (random.randint(0, __WIDTH), random.randint(0, __HEIGHT))
        if valid(m):
            nodes.append(m)
    return {i: {'x': m[0], 'y': m[1]} for i, m in enumerate(nodes)}


def random_planar_graph(n: int, connected=True, s=0.3) -> nx.Graph:
    """Generate a random planar graph.

    Parameters
    ----------
    n : int
        The number of nodes.

    connected : bool
        If `True`, the graph must be connected. Otherwise, it may be connected or disconnected.

    s : float
        A sparseness parameter between 0 (no edges) and 1 (many edges).

    Returns
    -------
    G : networkx Graph
        A random planar graph.

    Notes
    -----
    If `s` is set to `0.0`, the graph will only have `0` or `1` edges.
    Higher values encourage more edges to be added.
    A value of `1.0` will aim to add as many edges as possible.
    As n increases, so must sparseness.
    """
    assert n >= 0
    assert 0.0 <= s <= 1.0

    # Set the coordinates of the nodes.
    positions = __random_positions(n)
    cg = nx.complete_graph(n)
    nx.set_node_attributes(cg, positions)

    def coord(v):
        return cg.nodes[v]['x'], cg.nodes[v]['y']

    def dist(e):
        return math.dist(coord(e[0]), coord(e[1]))

    # Sort the edges according to the distance between their endpoints.
    edges = sorted(cg.edges(), key=dist)

    # Construct the final graph.
    result = nx.Graph()

    def coords(e):
        return [coord(e[0]), coord(e[1])]

    def keeps_planarity(new_edge):
        for e in result.edges:
            if e[0] in new_edge or e[1] in new_edge:
                continue
            l0 = LineString(coords(e))
            l1 = LineString(coords(new_edge))
            if l0.intersects(l1):
                return False
        return True

    def vector(v0, v1):
        v = np.array(v1) - np.array(v0)
        return v / np.linalg.norm(v)

    def large_angle(v0, v1):
        if v0 not in result:
            return True
        for v in nx.neighbors(result, v0):
            vec_0 = vector(coord(v0), coord(v))
            vec_1 = vector(coord(v0), coord(v1))
            angle = np.arccos(np.clip(np.dot(vec_0, vec_1), -1.0, 1.0))
            if angle <= __ANGLE_TOLERANCE:
                return False
        return True

    def large_angles(new_edge):
        v0, v1 = new_edge
        return large_angle(v0, v1) and large_angle(v1, v0)

    for i, edge in enumerate(edges):
        if keeps_planarity(edge) and large_angles(edge):
            result.add_edge(edge[0], edge[1])
        if result.number_of_nodes() == n and \
                i > s * len(edges) and \
                (not connected or nx.is_connected(result)):
            break

    new_positions = {p: v for p, v in positions.items() if p in result.nodes}
    nx.set_node_attributes(result, new_positions)
    return result
