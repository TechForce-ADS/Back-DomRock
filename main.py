import pandas as pd
from textblob import TextBlob
import numpy as np
import seaborn as sns
import re
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
import os
from dotenv import load_dotenv
import nltk
import matplotlib.pyplot as plt
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

nltk.download('wordnet')
from nltk.corpus import wordnet

# Função para pré-processar o texto
def preprocess_text(text):
    text = text.lower()  # Converte para minúsculas
    text = re.sub(r'\W+', ' ', text)  # Remove caracteres especiais
    return text

# Função para expandir a query com sinônimos
def expand_query(query):
    synonyms = set()
    for syn in wordnet.synsets(query):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())  # Adiciona sinônimos à lista
    return list(synonyms) if synonyms else [query]  # Retorna a query original se não houver sinônimos

# Carrega o CSV com os dados pré-processados
data = pd.read_csv("./dataset_preprocessed.csv")

# Transforma a coluna de nota em inteiros.
data["overall_rating"] = data["overall_rating"].str[-1].astype(int)

# Cria a coluna "overall_mean" com a média das avalições das reviews. 
data['overall_mean'] = data.groupby('product_name')['overall_rating'].transform('mean')

# Cria nova lista onde cada elemento é um chunk contendo o nome e a review
new_data = []
for index, row in data.iterrows():
    result = f"item {index}: {row.product_name}. review: {row.review_text}, categoria-1:{row.site_category_lv1}, categoria-2:{row.site_category_lv2}, sexo:{row.reviewer_gender}, estado:{row.reviewer_state}, media:{row.overall_mean}"
    new_data.append(preprocess_text(result))

# Carrega o modelo pré-treinado para gerar embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Transforma cada pedaço de texto em vetores
embeddings = model.encode(new_data)

# Configura o FAISS
d = embeddings.shape[1]  # Dimensão dos embeddings
index = faiss.IndexFlatL2(d)  # Índice de busca utilizando distância L2 (euclidiana)

# Adiciona os vetores ao índice
index.add(np.array(embeddings, dtype='float32'))

# Armazena os textos originais em um dicionário para recuperação posterior
id_to_document = {i: doc for i, doc in enumerate(new_data)}

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a API com a chave
genai.configure(api_key=os.getenv("API_KEY"))

# Função para determinar o sentimento (positivo, neutro, negativo)
def get_sentiment(text):
    analysis = TextBlob(text)
    # Define os thresholds para classificação de polaridade
    if analysis.sentiment.polarity > 0.1:
        return 'positivo'
    elif analysis.sentiment.polarity < -0.1:
        return 'negativo'
    else:
        return 'neutro'

# Adiciona uma nova coluna 'sentiment' com a classificação de sentimento
data['sentiment'] = data['review_text'].apply(get_sentiment)

# Agrupar os resultados por produto para determinar o sentimento predominante
sentiment_summary = data.groupby('product_name')['sentiment'].apply(lambda x: x.mode()[0])

# Função para gerar o gráfico de sentimento
def gerar_grafico_sentimento(sentiment_summary):
    # Contagem do número de produtos para cada tipo de sentimento predominante
    sentiment_counts = sentiment_summary.value_counts()

    # Configuração do estilo do seaborn
    sns.set(style="whitegrid")

    # Criar um gráfico de barras para os sentimentos predominantes
    plt.figure(figsize=(10, 6))
    sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette="viridis")

    # Adicionar rótulos e título
    plt.title('Sentimento Predominante dos Produtos', fontsize=16)
    plt.xlabel('Sentimento', fontsize=14)
    plt.ylabel('Quantidade de Produtos', fontsize=14)

    # Mostrar os valores nas barras
    for i, value in enumerate(sentiment_counts.values):
        plt.text(i, value + 1, str(value), ha='center', va='bottom', fontsize=12)

    # Exibir o gráfico
    plt.show()

# Função para criar um prompt dinâmico
def create_dynamic_prompt(context_type, question_type):
    template = f"""
    Contexto: {{context}}

    Pergunta ({question_type}): {{input}}
    
    Baseado no contexto fornecido e no tipo de pergunta, forneça uma resposta clara e concisa.
    """
    return ChatPromptTemplate.from_template(template)

# Função para criar um prompt específico
def create_specific_prompt(context_type, question_type):
    template = f"""
    Você está recebendo informações sobre ({context_type}). Utilize essas informações para responder à pergunta a seguir:

    Contexto:
    {{context}}
    
    Pergunta ({question_type}):
    {{input}}
    
    Para responder forneça uma análise geral sobre o produto com base nas avaliações dos usuários. Destaque os principais aspectos positivos e negativos, explicando os pontos mais relevantes em um formato fluido e natural. Conclua com uma recomendação geral, mencionando para quem o produto seria mais adequado e possíveis pontos de atenção. Evite o uso de listas e mantenha o tom de conversa.

    """
    return ChatPromptTemplate.from_template(template)

# Loop para permitir múltiplas perguntas
while True:
    # Pergunta do usuário
    query = input("Digite a pergunta (ou 'sair' para encerrar, 'gerar gráfico' para ver o gráfico): ")

    # Verifica se o usuário deseja encerrar o loop
    if query.lower() == 'sair':
        print("Encerrando o programa.")
        break
    elif query.lower() == 'gerar gráfico':
        gerar_grafico_sentimento(sentiment_summary)
    else:
        # Pré-processa e expande a query do usuário
        processed_query = preprocess_text(query)
        expanded_query = expand_query(processed_query)

        # Vetoriza a pergunta do usuário (query)
        query_embedding = model.encode(expanded_query)

        # Faz uma busca semântica no índice FAISS, recuperando mais resultados para triagem
        k = 20  # Número maior de resultados a serem recuperados
        distances, indices = index.search(np.array(query_embedding, dtype='float32'), k)

        # Seleciona os textos dos resultados recuperados
        retrieved_docs = [id_to_document[idx] for idx in indices[0]]

        # Filtra os documentos com base em uma distância limite para relevância
        threshold_distance = 1.5  # Aumente o limite para incluir mais resultados
        relevant_docs = [doc for i, doc in enumerate(retrieved_docs) if distances[0][i] < threshold_distance]

        # Se nenhum documento passar pelo filtro, usa os resultados originais
        if not relevant_docs:
            relevant_docs = retrieved_docs

        # Junta os resultados em um texto só e forma o "contexto" da resposta
        context = "\n".join(relevant_docs)

        # Escolher o tipo de contexto e pergunta (ajuste conforme necessário)
        context_type = "Produto e Avaliações"
        question_type = "Consulta do Usuário"

        # Criar o prompt usando uma das funções
        prompt = create_specific_prompt(context_type, question_type).format(context=context, input=query)

        # Carrega o modelo que vai interpretar o prompt
        model_gemini = genai.GenerativeModel("gemini-1.5-flash")

        # Passa o prompt para gerar a resposta
        response = model_gemini.generate_content(prompt)

        # Imprime a resposta gerada
        print("Resposta:", response.text)
