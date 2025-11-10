import logging
import os
from typing import List, Tuple, Dict, Any
import ast 

from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import faiss

logger = logging.getLogger(__name__)

class KBAgent:

    _instance = None

    @staticmethod
    def get_agent() -> 'KBAgent':

        if KBAgent._instance is None:
            from ..container import AppContainer
            container = AppContainer()
            KBAgent._instance = container.kb_agent()
        return KBAgent._instance
    
    def __init__(
        self,
    ) -> None:
        _datapath = "data/medium_articles.csv"
        self._embeddings_cache = "data/cached_embeddings.npy"

        # Load model without re-downloading if cached
        self._model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2', cache_folder="data/cache/transformers")

        self._df: pd.DataFrame =  self._load_and_preprocess(_datapath)
        self._index, self._embeddings = self._build_faiss_index(self._df)


    def _load_and_preprocess(self, datapath: str) -> pd.DataFrame:
        logger.info("Loading KB data from CSV.")
        df: pd.DataFrame = pd.DataFrame()
        try:
            df = pd.read_csv(datapath, dtype=str)
            df.fillna("", inplace=True)

            # dedup - TODO: improve dedup logic, can be probproblematic for similar articles
            def noramlize_link(url: str) -> str:
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(url)
                return urlunparse((parsed._replace(query="")))
            
            df["story_norm"] = df["story"].apply(noramlize_link)        
            df = df.drop_duplicates(subset=["story_norm", "title"]).reset_index(drop=True)

            def parse_tags(tag_str: str) -> List[str]:
                try:
                    tags = ast.literal_eval(tag_str)
                    if isinstance(tags, list):
                        return [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]
                except Exception as e:
                    logger.warning(f"Failed to parse tags: {str(e)}")
                return []
            
            df["tags_list"] = df["tags"].apply(parse_tags)
            
            df["text_for_embedding"] = (
                df["title"].str.strip() + ". " +
                df["subtitle"].str.strip() + ". Tags: " +
                df["tags_list"].apply(lambda tags: ", ".join(tags)) + ". Author: " +
                df["author"].str.strip()
            )
        except Exception as e:
            logger.error(f"Error loading KB data: {str(e)}")
            df = pd.DataFrame(columns=["title", "subtitle", "author", "date", "tags", "story", "tags_list", "text_for_embedding"])
        
        return df
    
    def _build_faiss_index(self, df: pd.DataFrame) -> Tuple[faiss.IndexFlatIP, np.ndarray]:
        logger.info("Building FAISS index for KB documents.")
        try:
            # Check for cached embeddings
            if os.path.exists(self._embeddings_cache):
                logger.info("Loading cached embeddings")
                embeddings = np.load(self._embeddings_cache)
            else:
                logger.warning("No cached embeddings found! Run preprocess_kb.py first")
                raise RuntimeError("Embeddings not found. Run preprocessing first.")
        
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings)
            
            return index, embeddings
        except Exception as e:
            logger.error(f"Error building FAISS index: {str(e)}")
        
        dimension = 384  # all-MiniLM-L6-v2 embedding size
        return faiss.IndexFlatIP(dimension), np.array([])
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"Searching KB for query: {query}")
        query_embedding: np.ndarray = self._model.encode(
            [query],
            normalize_embeddings=True
        ).astype(np.float32)
        
        distances, indices = self._index.search(query_embedding, top_k)
        
        results: List[Dict[str, Any]] = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self._df):
                row = self._df.iloc[idx]
                results.append({
                    "title": row["title"],
                    "subtitle": row["subtitle"],
                    "author": row["author"],
                    "date": row["date"],
                    "tags": row["tags_list"],
                    "link": row["story"],
                    "distance": float(distance)
                })
        
        return results

