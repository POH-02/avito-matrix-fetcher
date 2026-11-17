import asyncio
from matrix_fetcher import get_matrix, NetworkError, ParseError


async def main():
    url = 'https://raw.githubusercontent.com/avito-tech/python-trainee-assignment/main/matrix.txt'
    
    print(f"Загрузка матрицы с:\n{url}\n")
    
    try:
        result = await get_matrix(url)
        print("Результат обхода по спирали (против часовой стрелки):")
        print(result)
        print(f"\nКоличество элементов: {len(result)}")
    except NetworkError as e:
        print(f"Сетевая ошибка: {e}")
    except ParseError as e:
        print(f"Ошибка формата: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())