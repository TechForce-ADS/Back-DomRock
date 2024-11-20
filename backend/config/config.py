import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
MAX_HISTORY = 20
DATABASE_URL = "postgres://qqllikhg:V-fey-nz9fsIllukqM8khqrBNX_A5vYJ@bubble.db.elephantsql.com/qqllikhg"
SECRET_KEY = os.getenv("SECRET_KEY")
