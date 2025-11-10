import os
import ast
from typing import List
import logging
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_kb():

    datapath = "data/medium_articles.csv"
    cache_dir = "data/"
    embeddings_cache = os.path.join(cache_dir, "cached_embeddings.npy")

    if os.path.exists(embeddings_cache):
        logger.info(f"Embeddings cache found at {embeddings_cache}, skipping preprocessing.")
        return  
        
    os.makedirs(cache_dir, exist_ok=True)
    
    # Check for CUDA
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")

    # Load model with GPU support
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.to(device)
    
    try:
        # Load and process DataFrame similar to KB agent
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

        # Generate embeddings with GPU acceleration
        logger.info(f"Generating embeddings for {len(df)} documents...")
        embeddings = model.encode(
            df["text_for_embedding"].tolist(),
            batch_size=128,  # Increased batch size for GPU
            show_progress_bar=True,
            normalize_embeddings=True,
            device=device
        ).astype(np.float32)

        # Save embeddings
        np.save(embeddings_cache, embeddings)
        logger.info(f"Saved embeddings to {embeddings_cache}")
        
    except Exception as e:
        logger.error(f"Error in preprocessing: {str(e)}")
        raise

if __name__ == "__main__":
    preprocess_kb()