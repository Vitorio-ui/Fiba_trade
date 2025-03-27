from decimal import Decimal, getcontext
from utils.logger import setup_logger

logger = setup_logger()
getcontext().prec = 8  # Устанавливаем точность вычислений

class FundAllocator:
    @staticmethod
    def calculate_allocations(signals, total_deposit):
        """
        Рассчитывает распределение средств с защитой от ошибок
        """
        try:
            # Преобразуем total_deposit в Decimal, если это еще не сделано
            if not isinstance(total_deposit, Decimal):
                total_deposit = Decimal(str(total_deposit))
            
            deposit_percentage = Decimal('0.1')  # 10% от депозита
            base_amount = (total_deposit * deposit_percentage).quantize(Decimal('0.00000001'))
            
            ticker_groups = {}
            
            # Группируем сигналы по тикерам
            for signal in signals:
                if signal['ticker'] not in ticker_groups:
                    ticker_groups[signal['ticker']] = []
                ticker_groups[signal['ticker']].append(signal)
            
            allocations = []
            for ticker, ticker_signals in ticker_groups.items():
                group_count = len(ticker_signals)
                
                # Определяем коэффициенты распределения
                if group_count == 3:
                    ratios = [Decimal('0.2'), Decimal('0.3'), Decimal('0.5')]
                elif group_count == 2:
                    ratios = [Decimal('0.5'), Decimal('0.5')]
                else:
                    ratios = [Decimal('1')]
                
                for i, signal in enumerate(ticker_signals):
                    if i < len(ratios):
                        allocated = (base_amount * ratios[i]).quantize(Decimal('0.00000001'))
                        allocations.append({
                            'row': signal['row'],
                            'ticker': ticker,
                            'amount': float(allocated),
                            'entry_price': signal['entry_price']
                        })
            
            return allocations
            
        except Exception as e:
            logger.error(f"Ошибка расчета распределения средств: {str(e)}")
            return []