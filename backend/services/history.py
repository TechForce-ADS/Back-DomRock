from collections import deque
from config.config import MAX_HISTORY

history = deque(maxlen=MAX_HISTORY)

def add_to_history(role, message):
    history.append({"role": role, "message": message})

def get_chat_history():
    return "\n".join([f"{msg['role']}: {msg['message']}" for msg in history])
