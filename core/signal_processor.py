from utils.logger import setup_logger
from utils.exceptions import InvalidSignalError
from decimal import Decimal, getcontext
import math

logger = setup_logger()
getcontext().prec = 8

class SignalProcessor:
	def __init__(self, excel_manager):
		self.excel = excel_manager
	
	def get_active_signals(self):
		"""Получение активных сигналов с улучшенной проверкой"""
		signals = []
		for row in range(6, self.excel.sheet.max_row + 1):
			try:
				status = str(self.excel.sheet[f"B{row}"].value).strip().lower()
				if status in ['в работе', 'в_работе', 'active']:  # Все возможные варианты
					signal = self._parse_signal(row)
					if signal:
						signals.append(signal)
			except Exception as e:
				logger.warning(f"Ошибка обработки строки {row}: {str(e)}")
		return signals
	
	def _parse_signal(self, row):
		"""Парсит сигнал из строки Excel"""
		try:
			return {
				'row': row,
				'date': self._get_cell_value(row, 'A'),
				'status': self._get_cell_value(row, 'B'),
				'ticker': self._get_cell_value(row, 'C'),
				'current_price': Decimal(str(self._get_cell_value(row, 'D') or 0)),
				'entry_price': Decimal(str(self._get_cell_value(row, 'F') or 0)),
				'exit_price': Decimal(str(self._get_cell_value(row, 'G') or 0)),
				'planned_amount': Decimal(str(self._get_cell_value(row, 'I') or 0))
			}
		except Exception as e:
			raise InvalidSignalError(f"Ошибка парсинга строки {row}: {str(e)}")
	
	def _get_cell_value(self, row, column):
		"""Безопасное получение значения ячейки"""
		cell = f"{column}{row}"
		return self.excel.sheet[cell].value if self.excel.sheet[cell].value else None
	
	def update_signal_status(self, row, status):
		"""Обновляет статус сигнала"""
		try:
			self.excel.sheet[f"B{row}"] = status
			self.excel.save()
			logger.debug(f"Обновлен статус строки {row} на '{status}'")
		except Exception as e:
			raise InvalidSignalError(f"Ошибка обновления статуса: {str(e)}")
            
	def get_active_signals(self):
		"""Получение активных сигналов с улучшенной проверкой"""
		signals = []
		for row in range(6, self.excel.sheet.max_row + 1):
			try:
				status = str(self.excel.sheet[f"B{row}"].value).strip().lower()
				if status in ['в работе', 'active']:  # Все возможные варианты статуса
					signal = self._parse_signal(row)
					if signal:
						signals.append(signal)
			except Exception as e:
				logger.warning(f"Ошибка обработки строки {row}: {str(e)}")
		return signals