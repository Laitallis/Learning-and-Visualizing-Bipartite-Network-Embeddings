import sys
import json
import random
import logging
import argparse
from networkx.readwrite import json_graph

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', type=str, default="cora", help='set the dataset string name: cora, citeseer, tencent')
parser.add_argument('--walk_len', type=int, default=5, help='Walk length per node')
parser.add_argument('--n_walks', type=int, default=50, help='Walk times per node')
args = parser.parse_args()

walk_len = args.walk_len
n_walks = args.n_walks

def run_random_walks(G, nodes, walk_len, n_walks):
    pairs = []
    for count, node in enumerate(nodes):
        if G.degree(node) == 0:
            continue
        for i in range(n_walks):
            curr_node = node
            for j in range(walk_len):
                # to run this line, we must specify the networkx library version to <= 1.11
                next_node = random.choice(G.neighbors(curr_node))
                # self co-occurrences are useless
                if curr_node != node:
                    pairs.append((node, curr_node))
                curr_node = next_node
        if count % 1000 == 0:
            logging.info('Done walks for {:d} nodes'.format(count))
            print("Done walks for", count, "nodes")
    return pairs


if __name__ == "__main__":
    dataset_name = args.dataset
    logging.basicConfig(filename='run_graphsage_data_loader.log', filemode='w',
                        format='%(asctime)s  %(filename)s : %(lineno)d : %(levelname)s  %(message)s',
                        datefmt='%Y-%m-%d %A %H:%M:%S',
                        level=logging.INFO)

    """ Run random walks """
    graph_file = "./" + dataset_name + "/bipartite-G.json"
    out_file = "./" + dataset_name + "/bipartite-walks.txt"
    print(graph_file)
    print(out_file)
    logging.info('loading data...')
    G_data = json.load(open(graph_file))
    logging.info('converting to networkx')
    G = json_graph.node_link_graph(G_data)
    logging.info('extracting nodes...')
    nodes = [n for n in G.nodes() if not G.node[n]["val"] and not G.node[n]["test"]]
    G = G.subgraph(nodes)
    print('start random walk')
    logging.info('start random walk')
    pairs = run_random_walks(G, nodes, walk_len, n_walks)
    print('writting walks to file')
    with open(out_file, "w") as fp:
        fp.write("\n".join([str(p[0]) + "\t" + str(p[1]) for p in pairs]))
    logging.info('finished random walk')
    print('finished random walk')
