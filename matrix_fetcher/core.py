import asyncio
import logging
from typing import List

import httpx

from .exceptions import NetworkError, ParseError

logger = logging.getLogger(__name__)


def parse_matrix(text: str) -> List[List[int]]:
    """
    Парсит текстовое представление матрицы в двумерный список целых чисел.
    Игнорирует строки границ, состоящие из '+' и '-'.
    """
    lines = text.strip().split('\n')
    matrix = []
    
    for line in lines:
        line = line.strip()
        # Пропускаем строки границ и пустые строки
        if not line or line.startswith('+'):
            continue
        
        # Разделяем по '|' и фильтруем пустые элементы
        parts = [part.strip() for part in line.split('|') if part.strip()]
        if not parts:
            continue
            
        try:
            row = [int(x) for x in parts]
            matrix.append(row)
        except ValueError as e:
            raise ParseError(f"Не удалось преобразовать элемент в число в строке: {line}") from e

    if not matrix:
        raise ParseError("Матрица пуста или имеет неверный формат.")

    # Проверка на квадратность (NxN)
    n = len(matrix)
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ParseError(f"Матрица не является квадратной. Ожидалось {n} столбцов, получено {len(row)} в строке {i}.")

    return matrix


def traverse_spiral_ccw(matrix: List[List[int]]) -> List[int]:
    """
    Осуществляет обход квадратной матрицы по спирали против часовой стрелки,
    начиная с левого верхнего угла.
    """
    if not matrix:
        return []

    n = len(matrix)
    top, bottom, left, right = 0, n - 1, 0, n - 1
    result = []

    while top <= bottom and left <= right:
        # 1. Вниз по левому столбцу
        for i in range(top, bottom + 1):
            result.append(matrix[i][left])
        left += 1

        # 2. Вправо по нижней строке
        for i in range(left, right + 1):
            result.append(matrix[bottom][i])
        bottom -= 1

        # 3. Вверх по правому столбцу
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][right])
            right -= 1

        # 4. Влево по верхней строке
        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(matrix[top][i])
            top += 1

    return result


async def get_matrix(url: str) -> List[int]:
    """
    Получает квадратную матрицу с удаленного сервера по URL и возвращает 
    результат её обхода по спирали против часовой стрелки.
    """
    # Настраиваем таймауты для корректной обработки зависших соединений
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
    except httpx.HTTPStatusError as e:
        raise NetworkError(f"HTTP ошибка: {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.RequestError as e:
        raise NetworkError(f"Сетевая ошибка: {str(e)}") from e
    except asyncio.TimeoutError:
        raise NetworkError("Превышено время ожидания ответа от сервера") from e

    try:
        matrix = parse_matrix(text)
    except ParseError as e:
        raise ParseError(f"Ошибка парсинга матрицы: {e}") from e

    return traverse_spiral_ccw(matrix)