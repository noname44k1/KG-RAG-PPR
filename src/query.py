import os
import json
import numpy as np
import time
import asyncio
import argparse

from nano_graphrag import QueryParam
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

def log_process(i, question):
    with open(LOG_PROCESS_FILE, 'a') as f:
        f.write(f"done: {i} {question}\n")
def insert(docs, sindex, eindex):
    from time import time
    start = time()
    for i,doc in enumerate(docs[sindex:eindex], start=sindex):
        rag.insert(doc)
        log_process(i)
    print("indexing time:", time() - start)

def save_result(sample, response:str, chunk_list:list[str]):
    result={
        "question": list(sample.values())[0]['question'],
        "answer": list(sample.values())[0]['ground_truth'],
        "predicted_answer": response,
        "chunks": chunk_list,
        }
    with open(RESULT_FILE, "a") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
        f.write(",\n")


def query(samples,sindex, eindex):
    from time import time
    start = time()
    for i, sample in enumerate(samples[sindex:eindex], start=sindex): 
        # my query
        response, chunk_list = rag.query(
            list(sample.values())[0]["question"],
            param=QueryParam(
                # mode="my_query",local
                mode="my_query",
                top_k_triples= 5,
                top_k_chunks=10,
                chunk_weight = 0.19,
                damping_factor= 0.6,
                num_context_chunks= 40,
                k_hops = 3,
                k_paths = 3
            )
        )
        log_process(i,list(sample.values())[0]["question"])
        save_result(sample, response, chunk_list)
    print("query time:", time() - start)

if __name__ == "__main__":
    with open(samples_dir, "r") as f:
        samples = json.load(f)
    samples_list = []
    for k,v in samples.items():
        sample={k:v}
        samples_list.append(sample)

    query(samples_list, sindex, eindex)