from utils.logger import setup_logger
from utils.exceptions import InsufficientBalanceError, APIError
from decimal import Decimal

logger = setup_logger()

class OrderExecutor:
    def __init__(self, api_client, excel_manager, dry_run=True):
        self.api = api_client
        self.excel = excel_manager
        self.dry_run = dry_run
        logger.info(f"Инициализирован OrderExecutor (режим {'тестовый' if dry_run else 'боевой'})")

    def place_take_profit_buy(self, symbol, price, quantity, row):
        """Размещение тейк-профит ордера на покупку"""
        try:
            logger.info(f"Обработка TP BUY: {symbol} {quantity}@{price} (строка {row})")
            
            if self.dry_run:
                self.excel.simulate_order("BUY", row, price, quantity)
                return {"status": "simulated", "orderId": f"SIM_{symbol}_{row}"}
            
            # Реальная логика (не выполняется в тестовом режиме)
            usdt_balance = self._get_usdt_balance()
            required = Decimal(price) * Decimal(quantity)
            
            if usdt_balance < required:
                raise InsufficientBalanceError(
                    f"Недостаточно USDT. Нужно: {required}, есть: {usdt_balance}"
                )
            
            response = self.api.place_order(
                symbol=symbol,
                side="BUY",
                type="TAKE_PROFIT",
                quantity=quantity,
                price=price,
                stopPrice=price
            )
            
            logger.info(f"Ордер размещен: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при размещении TP BUY: {str(e)}")
            raise APIError(f"Ошибка ордера: {str(e)}")

    def place_limit_sell(self, symbol, price, quantity, row):
        """Размещение лимитного ордера на продажу"""
        try:
            logger.info(f"Обработка SELL: {symbol} {quantity}@{price} (строка {row})")
            
            if self.dry_run:
                self.excel.simulate_order("SELL", row, price, quantity)
                return {"status": "simulated", "orderId": f"SIM_{symbol}_{row}"}
            
            # Реальная логика (не выполняется в тестовом режиме)
            response = self.api.place_order(
                symbol=symbol,
                side="SELL",
                type="LIMIT",
                quantity=quantity,
                price=price
            )
            
            logger.info(f"Ордер размещен: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при размещении SELL: {str(e)}")
            raise APIError(f"Ошибка ордера: {str(e)}")

    def _get_usdt_balance(self):
        """Получает баланс USDT"""
        balance = self.api.get_account_balance()
        return Decimal(balance["USDT"]["free"])