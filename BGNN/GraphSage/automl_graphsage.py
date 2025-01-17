import argparse
import logging
import os
import queue
import random
import socket
import sys

import psutil
import setproctitle
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if __name__ == "__main__":
    setproctitle.setproctitle("BGNN:" + str(rank))

    logging.basicConfig(filename="./Graphsage.log_embedding",
                        level=logging.INFO,
                        format=str(rank) + ' - %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')

    hostname = socket.gethostname()
    logging.debug("#############process ID = " + str(rank) +
                  ", host name = " + hostname + "########" +
                  ", process ID = " + str(os.getpid()) +
                  ", process Name = " + str(psutil.Process(os.getpid())))

    # 972 parallel processes
    hpo_batch_size = [400, 500, 600, 700]  # 3
    hpo_epochs = [2, 3, 4]  # 4
    hpo_lr = [0.0002, 0.0003, 0.0004]  # 3
    hpo_weight_decay = [0.001, 0.0005, 0.0008]  # 3
    first_layer_dim = [32, 64, 128]
    hpo_dropout = [0.35, 0.4, 0.45]  # 3

    hpo_cnt = 0
    paras = dict()
    for batch_size in hpo_batch_size:
        for epochs in hpo_epochs:
            for lr in hpo_lr:
                for weight_decay in hpo_weight_decay:
                    for first_dim in first_layer_dim:
                        for dropout in hpo_dropout:
                            paras[hpo_cnt] = (batch_size, epochs, lr, weight_decay, first_dim, dropout)
                            hpo_cnt += 1

    (batch_size, epochs, lr, weight_decay, first_dim, dropout) = paras[rank]

    print("start hgcn_cmd")
    hgcn_cmd = "/mnt/shared/etc/anaconda3/bin/python3 /mnt/shared/home/bipartite-graph-learning/GraphSage/graphsage/unsupervised_train.py" \
               "--model graphsage --batch_size %d --epochs %d --learning_rate %f --weight_decay %f --dim_1 %d " \
               "--dropout %f --rank %d" % (
                   batch_size,
                   epochs,
                   lr,
                   weight_decay,
                   first_dim,
                   dropout,
                   rank)
    os.system(hgcn_cmd)
    print("end hgcn_cmd")

    print("start lr_cmd")
    lr_cmd = "/mnt/shared/etc/anaconda3/bin/python3 /mnt/shared/home/bipartite-graph-learning/Graphsage/binary_classification.py --rank %s" % rank
    os.system(lr_cmd)
    print("end lr_cmd")
