from flask import jsonify
from app import get_db_connection
from flask_login import current_user

def save_to_db(role, message):
    id = current_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO mensagem (msg_remetente, msg_texto, msg_conv_id) VALUES (%s, %s, (SELECT MAX(conv_id) FROM conversa WHERE conv_usu_id = %s) );",(role, message, id) )
    conn.commit()
    cur.close()
    conn.close()
    return "mensagem salva com sucesso"

def get_chat_history():
    id = current_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT msg_remetente as role, msg_texto as message FROM mensagem WHERE msg_conv_id = (SELECT MAX(conv_id) FROM conversa WHERE conv_usu_id = %s) ;",(id,) )
    res = cur.fetchall()
    cur.close()
    conn.close()    
    return res

def update_desc(mensagem):
    id = current_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT conv_desc FROM conversa WHERE conv_id = (SELECT MAX(conv_id) FROM conversa WHERE conv_usu_id = %s) ;",(id,) )
    res = cur.fetchone()
    if(res[0] in "conversa iniciada"):
        try:
            cur.execute("UPDATE conversa SET conv_desc = %s WHERE conv_id = (SELECT MAX(conv_id) FROM conversa WHERE conv_usu_id = %s) ;", ( mensagem , id) )
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"erro": "dados não encontrados"}), 404
            return jsonify({"mensagem": "dados atualizados"}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()
            
def listarConversasId():
    id = current_user.id 
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM conversa WHERE conv_usu_id = %s ORDER BY conv_id DESC ;",(id,) )
    res = cur.fetchall()
    cur.close()
    conn.close()    
    return res[1:]

def listarMensagens(conversa):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mensagem WHERE msg_conv_id = %s ORDER BY msg_id ASC ;",(conversa,) )
    res = cur.fetchall()
    cur.close()
    conn.close()    
    return res
