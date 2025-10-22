import os
import logging
import numpy as np
import asyncio
from dotenv import load_dotenv
import ollama
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize
import torch
from dataclasses import dataclass

from nano_graphrag import GraphRAG
from nano_graphrag.base import BaseVectorStorage
from nano_graphrag._utils import wrap_embedding_func_with_attrs
from nano_graphrag._storage import Neo4jStorage
from nano_graphrag._utils import logger
from llm_service import set_usage_file, gemini_model_if_cache, gpt_4o_complete, gpt_4o_mini_complete, gemini_complete

logging.basicConfig(level=logging.WARNING)
logging.getLogger("nano-graphrag").setLevel(logging.INFO)
load_dotenv(dotenv_path="/Users/khoi/Documents/DATN/.env")

# neo4j config
neo4j_config = {
  "neo4j_url": os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
  "neo4j_auth": (
      os.environ.get("NEO4J_USER", "neo4j"),
      os.environ.get("NEO4J_PASSWORD", "neo4jneo4j"),
  )
}

# Milvus config
@dataclass
class MilvusLiteStorge(BaseVectorStorage):

    @staticmethod
    def create_collection_if_not_exist(client, collection_name: str, **kwargs):
        if client.has_collection(collection_name):
            return
        # TODO add constants for ID max length to 32
        client.create_collection(
            collection_name, max_length=32, id_type="string", **kwargs
        )

    def __post_init__(self):
        from pymilvus import MilvusClient

        self._client_file_name = os.path.join(
            self.global_config["working_dir"], "milvus_lite.db"
        )
        self._client = MilvusClient(self._client_file_name)
        self._max_batch_size = self.global_config["embedding_batch_num"]
        MilvusLiteStorge.create_collection_if_not_exist(
            self._client,
            self.namespace,
            dimension=self.embedding_func.embedding_dim,
        )

    async def upsert(self, data: dict[str, dict]):
        logger.info(f"Inserting {len(data)} vectors to {self.namespace}")
        list_data = [
            {
                "id": k,
                **{k1: v1 for k1, v1 in v.items() if k1 in self.meta_fields},
            }
            for k, v in data.items()
        ]
        contents = [v["content"] for v in data.values()]
        batches = [
            contents[i : i + self._max_batch_size]
            for i in range(0, len(contents), self._max_batch_size)
        ]
        embeddings_list = await asyncio.gather(
            *[self.embedding_func(batch) for batch in batches]
        )
        embeddings = np.concatenate(embeddings_list)
        for i, d in enumerate(list_data):
            d["vector"] = embeddings[i]
        results = self._client.upsert(collection_name=self.namespace, data=list_data)
        return results

    async def query(self, query, top_k=5):
        embedding = await self.embedding_func([query])
        results = self._client.search(
            collection_name=self.namespace,
            data=embedding,
            limit=50,
            output_fields=list(self.meta_fields),
            # search_params={"metric_type": "COSINE", "params": {"radius": 0.2}},
            search_params={"metric_type": "COSINE"},
        )

        # Trích xuất khoảng cách và chuẩn hóa min-max
        distances = np.array([dp["distance"] for dp in results[0]])
        min_val = distances.min()
        max_val = distances.max()

        # Tránh chia cho 0 khi tất cả giá trị bằng nhau
        if max_val - min_val == 0:
            norm_scores = np.ones_like(distances)
        else:
            norm_scores = (distances - min_val) / (max_val - min_val)
        # Gắn lại điểm chuẩn hóa vào từng kết quả
        normalized_results = [
            {
                **{k: dp.get(k) for k in self.meta_fields},
                "id": dp["id"],
                "distance": norm_scores[i],
                # "normalized_score": norm_scores[i],
                #  "raw_score": dp["distance"]
            }
            for i, dp in enumerate(results[0])
        ]
        # Sắp xếp theo normalized_score giảm dần và lấy top_k
        top_results = sorted(normalized_results, key=lambda x: x["distance"], reverse=True)[:top_k]

        return top_results

semaphore_embedding = asyncio.Semaphore(1)
# sentence transformer model config
if torch.cuda.is_available():
    device="cuda"
    # os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"     
else: 
    device="mps"
    # os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
EMBED_MODEL = SentenceTransformer(
    "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
    # "BAAI/bge-m3", 
    device=device
)
@wrap_embedding_func_with_attrs(
    embedding_dim=EMBED_MODEL.get_sentence_embedding_dimension(),
    max_token_size=EMBED_MODEL.max_seq_length,
)
async def sentence_transformer_embedding(texts: list[str]) -> np.ndarray:
    async with semaphore_embedding:
        #vietnamese tokenizer
        texts = [tokenize(text) for text in texts]
        return EMBED_MODEL.encode(texts, normalize_embeddings=True)

# # ollama embedding config
# EMBEDDING_MODEL = "nomic-embed-text"
# EMBEDDING_MODEL_DIM = 768
# EMBEDDING_MODEL_MAX_TOKENS = 8192
# @wrap_embedding_func_with_attrs(
#     embedding_dim=EMBEDDING_MODEL_DIM,
#     max_token_size=EMBEDDING_MODEL_MAX_TOKENS,
# )
# async def ollama_embedding(texts: list[str]) -> np.ndarray:
#     embed_text = []
#     for text in texts:
#         data = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
#         embed_text.append(data["embedding"])

#     return embed_text

def rag_instance(WORKING_DIR, USAGE_FILE=None):
    if USAGE_FILE is not None:
        set_usage_file(USAGE_FILE)
    rag = GraphRAG(
        working_dir=WORKING_DIR,
        graph_storage_cls=Neo4jStorage,
        addon_params=neo4j_config,
        vector_db_storage_cls=MilvusLiteStorge,
        embedding_func=sentence_transformer_embedding,
        best_model_func=gemini_model_if_cache,
        cheap_model_func=gemini_model_if_cache,
    )
    return rag
