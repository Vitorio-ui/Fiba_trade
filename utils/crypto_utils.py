import os
import json
from cryptography.fernet import Fernet
from utils.logger import setup_logger

logger = setup_logger()

def decrypt_keys():
    """Расшифровывает API ключи с абсолютными путями"""
    try:
        BASE_DIR = r"D:\mexc_trading_bot"
        CONFIG_DIR = os.path.join(BASE_DIR, "config")
        
        key_path = os.path.join(CONFIG_DIR, "secret.key")
        api_keys_path = os.path.join(CONFIG_DIR, "api_keys.json")
        
        logger.debug(f"Попытка чтения ключей из:\n- {key_path}\n- {api_keys_path}")
        
        with open(key_path, "rb") as key_file:
            key = key_file.read()
        
        with open(api_keys_path, "rb") as enc_file:
            encrypted_data = enc_file.read()
        
        cipher = Fernet(key)
        return json.loads(cipher.decrypt(encrypted_data).decode())
    
    except Exception as e:
        logger.critical(f"Ошибка при чтении ключей: {str(e)}")
        raise