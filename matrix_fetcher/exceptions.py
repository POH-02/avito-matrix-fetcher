class MatrixFetcherError(Exception):
    """Базовое исключение для всех ошибок библиотеки."""
    pass


class NetworkError(MatrixFetcherError):
    """Вызывается при сетевых ошибках или ошибках сервера (5xx, таймаут, отказ в соединении)."""
    pass


class ParseError(MatrixFetcherError):
    """Вызывается при невозможности распарсить полученный текст в квадратную матрицу."""
    pass