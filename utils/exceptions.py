class TradingError(Exception):
    """Базовое исключение для торговых операций"""
    pass

class InsufficientBalanceError(TradingError):
    """Недостаточно средств для ордера"""
    pass

class APIError(TradingError):
    """Ошибка API запроса"""
    pass

class InvalidSignalError(TradingError):
    """Некорректный сигнал в данных"""
    pass

class ExcelFormatError(TradingError):
    """Ошибка формата Excel файла"""
    pass