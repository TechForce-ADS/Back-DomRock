from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from preprocessing.preprocessing import preprocess_text, expand_query
from services.history import add_to_history, get_chat_history
from services.sentiment_analysis import get_sentiment
from model.embeddings import index, model, id_to_document
from model.prompting_settings import create_prompt
import google.generativeai as genai
from dotenv import load_dotenv

# Importe a função de configuração da API
from model.model_config import configure_api

# Configure a API ao iniciar o app
configure_api()

app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "http://localhost:8080"}})

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    add_to_history("User", user_query)

    processed_query = preprocess_text(user_query)
    expanded_query = expand_query(processed_query)
    query_embedding = model.encode(expanded_query)

    if len(query_embedding.shape) == 1:
        query_embedding = query_embedding.reshape(1, -1)

    distances, indices = index.search(np.array(query_embedding, dtype='float32'), 20)
    retrieved_docs = [id_to_document[idx] for idx in indices[0]]
    context = "\n".join(retrieved_docs)
    model_gemini = genai.GenerativeModel("gemini-1.5-flash")

    # Criar o prompt com os novos parâmetros
    prompt, temperature, _, top_k, top_p = create_prompt(context, user_query)

    # Chamada para gerar a resposta passando apenas os parâmetros aceitos
    response = model_gemini.generate_content(prompt)

    # Verificação se o retorno é válido
    if response and hasattr(response, 'text'):
        add_to_history("Chatbot", response.text)
    else:
        add_to_history("Chatbot", "Desculpe, não consegui gerar uma resposta.")

    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True)
