from utils.logger import setup_logger
from decimal import Decimal, InvalidOperation
from decimal import Decimal, getcontext
from config import DECIMAL_PRECISION, QUANTIZE_FORMAT
import config

# Установка точности вычислений
getcontext().prec = DECIMAL_PRECISION
logger = setup_logger()

class BalanceCalculator:
	
	@staticmethod
	def calculate_balance(transactions):
		balance = Decimal('0')
		for tx in transactions:
			amount = Decimal(str(tx['amount'])).quantize(Decimal(QUANTIZE_FORMAT))
			if tx['type'] == 'deposit':
				balance += amount
			elif tx['type'] == 'withdrawal':
				balance -= amount
		return balance.quantize(Decimal(QUANTIZE_FORMAT))
		
	@staticmethod
	def calculate_asset_balance(transactions, asset):
		asset_balance = Decimal('0')
		for tx in transactions:
			if tx['asset'] == asset:
				amount = Decimal(str(tx['amount'])).quantize(Decimal(QUANTIZE_FORMAT))
				if tx['type'] == 'deposit':
					asset_balance += amount
				elif tx['type'] == 'withdrawal':
					asset_balance -= amount
		return asset_balance.quantize(Decimal(QUANTIZE_FORMAT))
		
	def __init__(self, api_client):
		self.api = api_client
	
	def calculate_total_deposit(self):
		"""Расчет депозита с правильной обработкой структуры баланса"""
		try:
			account = self.api.get_account_balance()
			
			# Инициализация
			usdt_free = Decimal('0')
			usdt_locked = Decimal('0')
			equivalent = Decimal('0')
			
			# Обработка USDT баланса
			if 'USDT' in account:
				usdt_free = Decimal(account['USDT'].get('free', '0'))
				usdt_locked = Decimal(account['USDT'].get('locked', '0'))
			
			# Обработка других монет
			for coin, balance in account.items():
				if coin == 'USDT':
					continue
					
				try:
					free = Decimal(balance.get('free', '0'))
					locked = Decimal(balance.get('locked', '0'))
					amount = free + locked
					
					if amount > 0:
						prices = self.api.get_prices([f"{coin}USDT"])
						if prices and f"{coin}USDT" in prices:
							equivalent += amount * Decimal(str(prices[f"{coin}USDT"]))
				except Exception as e:
					logger.warning(f"Ошибка обработки {coin}: {str(e)}")
					continue
			
			return {
				"total": float(usdt_free + usdt_locked + equivalent),
				"free_usdt": float(usdt_free),
				"locked_usdt": float(usdt_locked),
				"equivalent": float(equivalent)
			}
			
		except Exception as e:
			logger.error(f"Ошибка расчета депозита: {str(e)}")
			return {
				"total": 0.0,
				"free_usdt": 0.0,
				"locked_usdt": 0.0,
				"equivalent": 0.0
			}