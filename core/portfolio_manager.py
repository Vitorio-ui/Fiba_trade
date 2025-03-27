from utils.logger import setup_logger
from core.balance_calculator import BalanceCalculator

logger = setup_logger()

class PortfolioManager:
    def __init__(self, api_client):
        self.calculator = BalanceCalculator(api_client)
        self.positions = {}
    
    def update_portfolio(self):
        try:
            deposit_info = self.calculator.calculate_total_deposit()
            
            # Здесь можно добавить логику для обновления информации о позициях
            # Например, сравнение с предыдущим состоянием
            
            return deposit_info
        
        except Exception as e:
            logger.error(f"Ошибка обновления портфеля: {str(e)}")
            raise