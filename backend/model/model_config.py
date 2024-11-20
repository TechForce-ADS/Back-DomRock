# model_config.py
import google.generativeai as genai
from config.config import API_KEY

def configure_api():
    genai.configure(api_key=API_KEY)


