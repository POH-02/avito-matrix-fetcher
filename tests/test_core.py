import asyncio
import pytest
import httpx
from unittest.mock import AsyncMock, patch

from matrix_fetcher import get_matrix, NetworkError, ParseError

SOURCE_URL = 'https://raw.githubusercontent.com/avito-tech/python-trainee-assignment/main/matrix.txt'
TRAVERSAL = [
    10, 50, 90, 130,
    140, 150, 160, 120,
    80, 40, 30, 20,
    60, 100, 110, 70,
]


@pytest.mark.asyncio
async def test_get_matrix_real():
    """Реальный запрос к тестовому URL из задания."""
    result = await get_matrix(SOURCE_URL)
    assert result == TRAVERSAL


@pytest.mark.asyncio
async def test_get_matrix_mocked_success():
    """Проверка успешного парсинга и обхода с мокированным ответом."""
    mock_response = AsyncMock()
    mock_response.text = """+-----+-----+-----+-----+
|  10 |  20 |  30 |  40 |
+-----+-----+-----+-----+
|  50 |  60 |  70 |  80 |
+-----+-----+-----+-----+
|  90 | 100 | 110 | 120 |
+-----+-----+-----+-----+
| 130 | 140 | 150 | 160 |
+-----+-----+-----+-----+"""
    mock_response.raise_for_status = AsyncMock()

    with patch('httpx.AsyncClient.get', return_value=mock_response):
        result = await get_matrix("http://fake.url")
        assert result == TRAVERSAL


@pytest.mark.asyncio
async def test_get_matrix_network_error():
    """Проверка обработки ошибки соединения (Connection Refused)."""
    with patch('httpx.AsyncClient.get', side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(NetworkError, match="Сетевая ошибка"):
            await get_matrix("http://fake.url")


@pytest.mark.asyncio
async def test_get_matrix_http_error():
    """Проверка обработки ошибок сервера (5xx)."""
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.reason_phrase = "Internal Server Error"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Server Error", request=AsyncMock(), response=mock_response
    )

    with patch('httpx.AsyncClient.get', return_value=mock_response):
        with pytest.raises(NetworkError, match="HTTP ошибка: 500"):
            await get_matrix("http://fake.url")


@pytest.mark.asyncio
async def test_get_matrix_parse_error():
    """Проверка обработки невалидного формата данных."""
    mock_response = AsyncMock()
    mock_response.text = "Это точно не матрица"
    mock_response.raise_for_status = AsyncMock()

    with patch('httpx.AsyncClient.get', return_value=mock_response):
        with pytest.raises(ParseError, match="Ошибка парсинга матрицы"):
            await get_matrix("http://fake.url")