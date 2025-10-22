import os
import json
import numpy as np
import time
import asyncio
import argparse

from base import rag_instance

parser = argparse.ArgumentParser()
parser.add_argument('--working_dir', type=str, required=True)
parser.add_argument('--sindex', type=int, required=True)
parser.add_argument('--eindex', type=int, required=True)
parser.add_argument('--usage', type=str, required=True)
parser.add_argument('--log', type=str, required=True)
parser.add_argument('--result_file', type=str, required=True)
parser.add_argument('--samples_dir', type=str, required=True)
parser.add_argument('--corpus_dir', type=str, required=True)
args = parser.parse_args()

WORKING_DIR= args.working_dir
sindex = args.sindex
eindex = args.eindex
USAGE_FILE= args.usage
LOG_PROCESS_FILE= args.log
RESULT_FILE= args.result_file
samples_dir = args.samples_dir
corpus_dir = args.corpus_dir

rag = rag_instance(WORKING_DIR, USAGE_FILE)

def log_process(i):
    with open(LOG_PROCESS_FILE, 'a') as f:
        f.write(f"done: {i}\n")
def insert(docs, sindex, eindex):
    from time import time
    start = time()
    for i,doc in enumerate(docs[sindex:eindex], start=sindex):
        rag.insert(doc)
        log_process(i)
    print("indexing time:", time() - start)

if __name__ == "__main__":
    # with open(samples_dir, "r") as f:
    #     samples = json.load(f)
    # all_queries = [s['question'] for s in samples]
    with open(corpus_dir, "r") as f:
        corpus = f.read()
    corpus_list = corpus.split("<SEP>")

    insert(corpus_list, sindex, eindex)