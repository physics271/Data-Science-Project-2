import networkx as nx

import scraper_functions

class GraphDisplay:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.visited_pages = dict()
        self.groups = 0

    def make_network(self, seed_num):
        self.visited_pages = scraper_functions.make_network(seed_num)

    def make_graph(self, pages):
        G = nx.DiGraph()
        graph_edges = [(node, dest) for node, dest in pages.items() if dest!=None]

        G.add_nodes_from((key, {'label':key, 'shape':'dot', 'size':10}) for key in pages.keys())
        G.add_edges_from(graph_edges)

        connected = nx.connected_components(G.to_undirected())
        group_num = 0

        for i, cc in enumerate(connected):
            group_num += 1
            for j, node in enumerate(cc):
                G.nodes[node]['group']=i
                G.nodes[node]['x']=300*i+0.01*j
            
            
        cycles = nx.simple_cycles(G)
        for cycle in cycles:
            for node in cycle:
                G.nodes[node]['size']=15
                G.nodes[node]['shape']='hexagon'

        return G, group_num

    def reset_graph(self, num=3):
        self.make_network(num)
        self.graph, self.groups = self.make_graph(self.visited_pages)

    def add_graph(self, seed_url=None):
        new_nodes, join_node = scraper_functions.add_to_network(self.visited_pages, seed=seed_url)
        self.visited_pages = dict(self.visited_pages, **new_nodes)
        new_edges = [(node, dest) for node, dest in new_nodes.items() if dest!=None]

        if join_node:
            G = self.graph
            group_num = G.nodes[join_node]['group']
            G.add_nodes_from((key, {
                'label':key, 
                'shape':'dot', 
                'size':10, 
                'group':group_num
            }) for key in new_nodes.keys())

            G.add_edges_from(new_edges)
        
        else:
            new_G, _ = self.make_graph(new_nodes)
            self.groups += 1

            for node in new_G.nodes:
                new_G.nodes[node]['group'] = self.groups
                new_G.nodes[node]['x'] = 300*self.groups

            union = nx.union(self.graph, new_G)

            union.add_edges_from(new_edges)

            self.graph = union

    
    def output_graph(self):
        nodes = [{'id':a, **b} for a, b in self.graph.nodes.data()]

        edges = [{'id':f'{a}-{b}', 'from':a, 'to':b, **c} for a, b, c in self.graph.edges.data()]

        return {'nodes':nodes, 'edges':edges}

    