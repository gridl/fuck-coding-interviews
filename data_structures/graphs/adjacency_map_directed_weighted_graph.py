# coding: utf-8
"""
Graph
https://en.wikipedia.org/wiki/Graph_(abstract_data_type)
https://en.wikipedia.org/wiki/Directed_graph
https://en.wikipedia.org/wiki/Adjacency_list

Assume that we have V vertices and E edges in the graph G.
"""
from collections import defaultdict
from collections import deque
import heapq


class NestedBreak(Exception):
    pass


# This implementation cannot properly handle multiple edges between the same endpoints.
# For instance, (u, v, 1), (u, v, 2) and (u, v, 3).
class DirectedGraph:
    def __init__(self):
        # {
        #     'source_vertex': {
        #         'destination_vertex': edge_weight,
        #     },
        # }
        self.outgoing_edges = defaultdict(dict)

        # {
        #     'vertex': data,
        # }
        self.vertex_data = {}

    def add_vertex(self, v, value=None):
        self.vertex_data[v] = value

    def add_edge(self, u, v, weight=None):
        # Make sure that both vertices are in the graph.
        self.vertex_data.setdefault(u)
        self.vertex_data.setdefault(v)
        self.outgoing_edges[u][v] = weight

    def remove_vertex(self, v):
        # Remove associate edges.
        del self.outgoing_edges[v]
        for _, incident_vertices in self.outgoing_edges.items():
            # NOTE: We use list(dict.keys()) to avoid
            # RuntimeError: dictionary changed size during iteration.
            for destination in list(incident_vertices.keys()):
                if destination == v:
                    del incident_vertices[destination]

        # Remove associate data.
        del self.vertex_data[v]

    def remove_edge(self, u, v):
        try:
            del self.outgoing_edges[u][v]
        except KeyError:
            raise ValueError(f'No such edge: {(u, v)}')

    def vertex_count(self):
        return len(self.vertex_data.keys())

    def edge_count(self):
        count = 0
        for _ in self.edges():
            count += 1
        return count

    def vertices(self):
        for vertex in self.vertex_data.keys():
            yield vertex

    def edges(self):
        for source, incident_edges in self.outgoing_edges.items():
            for destination, weight in incident_edges.items():
                yield (source, destination, weight)

    def incident_edges(self, v, edge_type='outgoing'):
        if edge_type == 'outgoing':
            try:
                for destination, weight in self.outgoing_edges[v].items():
                    yield (v, destination, weight)
            except KeyError:
                return []
        elif edge_type == 'incoming':
            for source, incident_vertices in self.outgoing_edges.items():
                for destination, weight in incident_vertices.items():
                    if destination == v:
                        yield (source, v, weight)

    def edge_weight(self, u, v):
        try:
            return self.outgoing_edges[u][v]
        except KeyError:
            raise ValueError(f'No such edge: {(u, v)}')

    def breadth_first_search(self, v):
        """
        Applications
        https://en.wikipedia.org/wiki/Breadth-first_search
        https://cp-algorithms.com/graph/breadth-first-search.html#toc-tgt-2
        """
        visited = set()
        current_level = [v, ]
        while current_level:
            next_level = []
            for node in current_level:
                # NOTE: A vertex is visited means we can access its adjacent vertices (neighbors).
                visited.add(node)
                for neighbor in self.outgoing_edges[node].keys():
                    if neighbor not in visited:
                        next_level.append(neighbor)

            current_level = next_level

        return visited

    def breadth_first_search_queue(self, v):  # pragma: no cover
        visited = set([v, ])
        queue = deque([v, ])
        while queue:
            node = queue.popleft()
            for neighbor in self.outgoing_edges[node].keys():
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited

    def depth_first_search(self, v, visited=None):
        if visited is None:
            visited = set()

        visited.add(v)
        for neighbor in self.outgoing_edges[v].keys():
            if neighbor not in visited:
                # Recursion uses the call "stack".
                self.depth_first_search(neighbor, visited)

        return visited

    def depth_first_search_iterate(self, v):  # pragma: no cover
        visited = set()
        stack = [v, ]
        while stack:
            node = stack.pop()
            visited.add(node)
            for neighbor in self.outgoing_edges[node].keys():
                if neighbor not in visited:
                    stack.append(neighbor)

        return visited

    def construct_path(self, backtracks, start, end):
        backtrack_path = [end, ]
        last_step = backtracks.get(end)
        while last_step:
            backtrack_path.append(last_step)
            last_step = backtracks[last_step]

        if backtrack_path[-1] != start:
            raise ValueError(f'No path from {start} to {end}')

        return list(reversed(backtrack_path))

    # O(V + E)
    def find_shortest_path_bfs(self, start, end):
        """
        This algorithm can only work with a unweighted graph.
        """
        backtracks = {v: None for v in self.vertex_data.keys()}
        visited = set([start, ])
        queue = deque([start, ])
        try:
            while queue:
                v = queue.popleft()
                for neighbor in self.outgoing_edges[v].keys():
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        backtracks[neighbor] = v
                        if neighbor == end:
                            raise NestedBreak
        except NestedBreak:
            pass

        return self.construct_path(backtracks, start, end)

    # O(E * log V)
    def find_shortest_path_dijkstra(self, start, end):
        """
        This algorithm can only work with a non-negative graph.
        https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
        https://leetcode.com/problems/network-delay-time/discuss/329376/efficient-oe-log-v-python-dijkstra-min-heap-with-explanation
        """
        # First, we overestimate the distance from start to all other vertices.
        distances = {}  # The distance from start to a vertex v.
        backtracks = {}  # {destination: source}
        for v in self.vertex_data.keys():
            distances[v] = float('inf')
            backtracks[v] = None
        distances[start] = 0

        # We maintain a priority queue to extract a vertex v which has the minimum distance.
        visited = set()
        min_heap = [(0, start), ]  # (distance, vertex)
        while min_heap:
            src_distance, src = heapq.heappop(min_heap)
            # A vertex could be added to the priority queue multiple times,
            # so we need to track visited vertices.
            visited.add(src)
            for des, weight in self.outgoing_edges[src].items():
                if des in visited:
                    continue
                distance_to_des = src_distance + weight
                if distance_to_des < distances[des]:
                    # We find a shorter path to des,
                    # so distances of its dess should also be readjust.
                    distances[des] = distance_to_des
                    backtracks[des] = src
                    heapq.heappush(min_heap, (distances[des], des))

        return self.construct_path(backtracks, start, end)

    # O(V * E)
    def find_shortest_path_bellman_ford(self, start, end):
        """
        This algorithm can only work with a graph which has no negative weight cycles.
        https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
        """
        # First, we overestimate the distance from start to all other vertices.
        distances = {}  # The distance from start to a vertex v.
        backtracks = {}  # {destination: source}
        for v in self.vertex_data.keys():
            distances[v] = float('inf')
            backtracks[v] = None
        distances[start] = 0

        # We have to do V * E times to readjust distances.
        vertex_count = self.vertex_count()
        # The first loop, it calculates the shortest paths with at most 1 edge.
        # Then, it calculates the shortest paths with at most 2 edges, and so on.
        for i in range(vertex_count):
            for src, des, weight in self.edges():
                distance_to_des = distances[src] + weight  # The distance to destination.
                if distance_to_des < distances[des]:
                    # The final loop is to check wheter there are negative weight cycles.
                    if i == vertex_count - 1:
                        raise ValueError('Found negative weight cycles')
                    distances[des] = distance_to_des
                    backtracks[des] = src

        return self.construct_path(backtracks, start, end)
