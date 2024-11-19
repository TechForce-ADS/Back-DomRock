from flask_login import UserMixin
from app import login_manager, get_db_connection

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT usu_id, usu_email FROM usuario WHERE usu_id = %s", (user_id,))
    user_data = cur.fetchone()
    conn.close()
    if user_data:
        return User(*user_data)
    return None