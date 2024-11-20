import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

data = pd.read_csv("./datasets/dataset_preprocessed.csv")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Caminho para o arquivo de embeddings
EMBEDDINGS_PATH = './datasets/embeddings.npy'

def get_embeddings(data):
    # Verifica se o arquivo de embeddings já existe
    if os.path.exists(EMBEDDINGS_PATH):
        print("Carregando embeddings existentes.")
        embeddings = np.load(EMBEDDINGS_PATH)
    else:
        print("Gerando novos embeddings.")
        embeddings = []
        for text in tqdm(data, desc="Gerando embeddings", unit="texto"):
            embeddings.append(model.encode(text))
        embeddings = np.array(embeddings)
        # Salva os embeddings para uso futuro
        np.save(EMBEDDINGS_PATH, embeddings)
    return embeddings


# Preparando os dados para a geração de embeddings
text_data = [
    f"item {index}: {row.product_name}. review: {row.review_text}, categoria-1: {row.site_category_lv1}, categoria-2: {row.site_category_lv2}"
    for index, row in data.iterrows()
]

# Carrega ou gera os embeddings
embeddings = get_embeddings(text_data)

# Configura o FAISS
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(np.array(embeddings, dtype='float32'))
id_to_document = {i: doc for i, doc in enumerate(text_data)}
