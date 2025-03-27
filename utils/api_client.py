import requests
import hmac
import hashlib
import time
import json
from urllib.parse import urlencode
from utils.logger import setup_logger
import config

logger = setup_logger()

class MEXCClient:
    def __init__(self):
        self.base_url = "https://api.mexc.com/api/v3"
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Загрузка API ключей"""
        try:
            from utils.crypto_utils import decrypt_keys
            keys = decrypt_keys()
            self.api_key = keys["api_key"]
            self.secret_key = keys["secret_key"]
        except Exception as e:
            logger.error(f"Ошибка загрузки API ключей: {str(e)}")
            raise

    def _sign_request(self, params):
        """Подпись запроса"""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(sorted(params.items()))
        signature = hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def get_account_balance(self):
        """Получение баланса с правильной обработкой структуры MEXC API v3"""
        try:
            params = self._sign_request({})
            response = requests.get(
                f"{self.base_url}/account",
                params=params,
                headers={"X-MEXC-APIKEY": self.api_key},
                timeout=config.API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            # Правильная обработка структуры MEXC API v3
            if not isinstance(data, dict) or 'balances' not in data:
                logger.error("Некорректный формат ответа от API")
                return {}
                
            # Преобразуем список балансов в словарь
            balances = {}
            for item in data['balances']:
                if isinstance(item, dict) and 'asset' in item:
                    balances[item['asset']] = {
                        'free': item.get('free', '0'),
                        'locked': item.get('locked', '0')
                    }
            return balances
            
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {str(e)}")
            return {}

    def get_prices(self, symbols):
        """Получение текущих цен для списка символов"""
        try:
            if not symbols:
                return {}

            params = {"symbols": json.dumps(symbols)}
            response = requests.get(
                f"{self.base_url}/ticker/price",
                params=params,
                timeout=config.API_TIMEOUT
            )
            response.raise_for_status()
            
            # Преобразуем ответ в удобный формат
            prices = {}
            for item in response.json():
                if isinstance(item, dict) and "symbol" in item and "price" in item:
                    prices[item["symbol"]] = float(item["price"])
            return prices
            
        except Exception as e:
            logger.error(f"Ошибка получения цен: {str(e)}")
            return {}