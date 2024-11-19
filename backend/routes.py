from app import app, get_db_connection
from flask import jsonify, redirect, request, flash, url_for
from services.history import get_chat_history, listarMensagens, save_to_db, update_desc, listarConversasId
from entity.user import User
import numpy as np
from model.prompting_settings import create_prompt
import google.generativeai as genai
from model.embeddings import index, model, id_to_document
from preprocessing.preprocessing import preprocess_text, expand_query
from flask_login import current_user, login_user, logout_user, login_required

#login passando email e senha pelo body da requisição
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dados = request.get_json()
        email = dados.get("email")
        senha = dados.get("senha")
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT usu_id, usu_email FROM usuario WHERE usu_email = %s AND usu_senha = %s", (email, senha))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
                
        if user_data:
            user = User(*user_data)
            login_user(user)
            flash("Login realizado com sucesso", "success")
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO conversa (conv_desc , conv_usu_id) VALUES ('conversa iniciada' , %s)",(current_user.id,) )
                conn.commit()
                return "Login realizado com sucesso"
            except Exception as e:
                conn.rollback()
                flash("falha ao inicar sessão.", "danger")
            finally:
                cur.close()
                conn.close()
        else:
            flash("Login falhou", "danger")
            return redirect(url_for("login"))
    
    return "texto qualquer teste"

#logout, finaliza a sessão
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Usuário desconectado.", "info")
    return redirect(url_for("login"))

#chat
@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    save_to_db("user", user_query)
    
    update_desc(user_query)
    
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
    
    if response and hasattr(response, 'text'):
        save_to_db('chat' , response.text)
    else:
        save_to_db('chat' , "Desculpe, não consegui gerar uma resposta.")
    return jsonify({'response': response.text})

#listar conversas do usuario logado
@app.route('/conversas', methods=['GET'])
def getConversas():
    return listarConversasId()

#listar mensagens da conversa selecionada , passar o id da conversa na url da rota
@app.route('/mensagens/<conversa>', methods=['GET'])
def getMensagens(conversa):
    return listarMensagens(conversa)



''' 
# daqui pra baixo é só teste, apagar depois de tudo testado------------------------------

@app.route('/userlogado', methods = ['GET'])
def getuserlogado():
    return str(current_user.id)


@app.route('/testehist', methods=['GET'])
def gethist():
    return get_chat_history()
    
'''