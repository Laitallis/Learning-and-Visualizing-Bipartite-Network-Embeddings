import argparse
import logging
import os

import conf


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--dataset', type=str, default='cora', required=True)
	parser.add_argument('--rank', type=int, default=-1,
						help='process ID for MPI Simple AutoML')

	return parser.parse_args()


if __name__ == "__main__":
	print("########## classification.py (START) ################")
	args = parse_args()
	dataset = args.dataset
	rank = args.rank

	# classification
	it = 3000
	method = "gae"

	input_folder = conf.input_folder + str(dataset)
	output_folder = conf.output_folder + "/" + str(dataset)

	if rank != -1:
		input_folder = "/mnt/shared/home/bipartite-graph-learning/data/" + str(dataset)
		output_folder = "/mnt/shared/home/bipartite-graph-learning/out/gae/"  + str(dataset) + "/" + str(rank)

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	emb_file = str(output_folder) + "/gae.emb"
	print(emb_file)

	# the BGNN node list is smaller than the raw node list because some illegal nodes are filtered
	hgcn_node_file = str(output_folder) + "/node_list"
	print(hgcn_node_file)

	res_file = str(output_folder) + "/gae.res"
	f = open(res_file, "+w")
	f.write("")
	f.close()
	print(res_file)

	# Performing example logistic regression
	if os.path.exists(emb_file):
		max_iter = 300
		if rank == -1:
			lr_cmd = "python3 ./classifier/multiclass_lr.py --verbose 0 --input_folder %s --emb_file %s --node_file %s --res_file %s --max_iter %d" % (
				input_folder,
				emb_file,
				hgcn_node_file,
				res_file,
				it)
		else:
			lr_cmd = "/mnt/shared/etc/anaconda3/bin/python3 /mnt/shared/home/bipartite-graph-learning/classifier/multiclass_lr.py --verbose 0 --input_folder %s --emb_file %s --node_file %s --res_file %s --max_iter %d" % (
				input_folder,
				emb_file,
				hgcn_node_file,
				res_file,
				it)

		os.system(lr_cmd)
	else:
		print("no emb file")
		logging.info("no emb file")
		exit(1)
	res_file = res_file + ".prec_rec"

	if os.path.exists(res_file):
		fin = open(res_file, 'r')
		ap = 0
		for l in fin:
			ap = ap + float(l.strip().split(' ')[-2])
		fout = open(os.path.join(output_folder, "result_file"), 'w')
		fout.write("object_value=%f" % (ap))
		fout.close()
	else:
		logging.info("No res file.")
		exit(1)

	print("########## classification.py (END) ################")
