import os
import sys
from decimal import Decimal
from utils.api_client import MEXCClient
from utils.logger import setup_logger
from core.excel_manager import ExcelManager
from core.order_executor import OrderExecutor
from core.balance_calculator import BalanceCalculator
from core.signal_processor import SignalProcessor
from strategies.allocation import FundAllocator
import config

# Настройка логгера
logger = setup_logger()

def initialize_components():
	"""Инициализация всех компонентов приложения"""
	try:
		# Проверка путей
		BASE_DIR = r"D:\mexc_trading_bot"
		CONFIG_DIR = os.path.join(BASE_DIR, "config")
		DATA_DIR = os.path.join(BASE_DIR, "data")
		EXCEL_PATH = os.path.join(DATA_DIR, "Fiba.xlsx")

		# Проверка существования файлов
		required_files = {
			"API ключи": os.path.join(CONFIG_DIR, "api_keys.json"),
			"Ключ шифрования": os.path.join(CONFIG_DIR, "secret.key"),
			"Excel файл": EXCEL_PATH
		}

		for name, path in required_files.items():
			if not os.path.exists(path):
				raise FileNotFoundError(f"{name} не найден: {path}")

		logger.info("=== НАСТРОЙКА СКРИПТА ===")
		logger.info(f"Работа с файлом: {EXCEL_PATH}")

		# Инициализация компонентов
		api = MEXCClient()
		excel = ExcelManager(EXCEL_PATH)
		portfolio = BalanceCalculator(api)
		signal_processor = SignalProcessor(excel)
		order_executor = OrderExecutor(api, excel, dry_run=config.DRY_RUN)

		return api, excel, portfolio, signal_processor, order_executor

	except Exception as e:
		logger.critical(f"Ошибка инициализации: {str(e)}")
		raise

def main():
	try:
		# Инициализация
		api, excel, portfolio, signal_processor, order_executor = initialize_components()

		# 1. Проверка подключения к API
		logger.info("\n=== ПРОВЕРКА ПОДКЛЮЧЕНИЯ ===")
		# Проверка структуры ответа API
		try:
			test_balance = api.get_account_balance()
			logger.debug(f"Структура ответа API: {test_balance}")
		except Exception as e:
			logger.error(f"Ошибка теста API: {str(e)}")
			return

		# 2. Расчет баланса
		logger.info("\n=== РАСЧЕТ БАЛАНСА ===")
		deposit_info = portfolio.calculate_total_deposit()
		logger.info(
			f"Общий баланс: {deposit_info['total']:.2f} USDT\n"
			f"- Свободно: {deposit_info['free_usdt']:.2f}\n"
			f"- Заблокировано: {deposit_info['locked_usdt']:.2f}\n"
			f"- Эквивалент: {deposit_info['equivalent']:.2f}"
		)

		if deposit_info['total'] < config.MIN_BALANCE and deposit_info['equivalent'] < config.MIN_EQUIVALENT:
			logger.error(
				f"Недостаточно средств:\n"
				f"Требуется: {config.MIN_BALANCE} USDT или {config.MIN_EQUIVALENT} эквивалента\n"
				f"Текущий баланс: {deposit_info['total']:.2f} USDT + {deposit_info['equivalent']:.2f} эквивалента"
			)
			return

		# 3. Обработка сигналов
		logger.info("\n=== ОБРАБОТКА СИГНАЛОВ ===")
		signals = signal_processor.get_active_signals()
		
		if not signals:
			logger.warning(
				"Нет активных сигналов. Проверьте:\n"
				"- Статус в колонке B (должно быть 'в работе')\n"
				"- Наличие данных в строках 6 и ниже\n"
				"- Корректность формата файла"
			)
			return

		logger.info(f"Найдено активных сигналов: {len(signals)}")

		# 4. Обновление цен
		active_tickers = list({s['ticker'] for s in signals})
		prices = api.get_prices(active_tickers)
		excel.update_prices(prices)
		logger.info(f"Обновлены цены для {len(prices)} тикеров")

		# 5. Распределение средств
		allocations = FundAllocator.calculate_allocations(
			signals,
			Decimal(str(deposit_info["total"])) if not isinstance(deposit_info["total"], Decimal) else deposit_info["total"]
			)
		
		for alloc in allocations:
			excel.sheet[f"I{alloc['row']}"] = float(alloc['amount'])
		logger.info(f"Распределены средства для {len(allocations)} сигналов")

		# 6. Обработка ордеров
		logger.info("\n=== ОБРАБОТКА ОРДЕРОВ ===")
		for signal in signals:
			try:
				if signal['status'] == 'в работе':
					order_executor.place_take_profit_buy(
						symbol=signal['ticker'],
						price=float(signal['entry_price']),
						quantity=float(signal['planned_amount'] / signal['entry_price']),
						row=signal['row']
					)
			except Exception as e:
				logger.error(f"Ошибка обработки сигнала в строке {signal['row']}: {str(e)}")
				continue

		# 7. Сохранение результатов
		excel.save()
		logger.info("\n=== РЕЗУЛЬТАТЫ ===")
		logger.info("Все данные успешно сохранены в Excel")

	except KeyboardInterrupt:
		logger.info("Скрипт остановлен пользователем")
	except Exception as e:
		logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}", exc_info=True)
	finally:
		logger.info("\n=== СКРИПТ ЗАВЕРШЕН ===")

if __name__ == "__main__":
	# Добавляем путь к проекту в PYTHONPATH
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))
	
	# Запуск главной функции
	main()