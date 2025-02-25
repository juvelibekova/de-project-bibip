from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        """ Создает директорию и файлы """
        parent_dir = Path(__file__).resolve().parent.parent
        folder_path = parent_dir / root_directory_path
        folder_path.mkdir(parents=True, exist_ok=True)

        files = [
            'cars.txt', 'cars_index.txt',
            'models.txt', 'models_index.txt',
            'sales.txt', 'sales_index.txt'
        ]

        # Создаем файлы
        for file_name in files:
            file_path = parent_dir / root_directory_path / file_name
            file_path.touch()

        self.root_directory_path = folder_path
        self.cars_index_path = folder_path / 'cars_index.txt'
        self.cars_data_path = folder_path / 'cars.txt'
        self.models_index_path = folder_path / 'models_index.txt'
        self.models_data_path = folder_path / 'models.txt'
        self.sales_index_path = folder_path / 'sales_index.txt'
        self.sales_data_path = folder_path / 'sales.txt'

    # Чтение файла с индексом
    def read_index(self, path):

        with open(path, "r") as f:
            try:
                index = json.load(f)
            except json.JSONDecodeError:
                index = []

        return index

    # Задание 1. Сохранение моделей
    def add_model(self, model: Model) -> Model:

        # Читам файл с индексами 
        with open(self.models_index_path, "r") as f:
            try:
                models_index = json.load(f)
            except json.JSONDecodeError:
                models_index = []

        # Проверяем, есть ли уже такой id в индексе
        for index in models_index:
            if index[0] == model.id:
                break
        # Если такого нет, добавляем пару "id - номер строки"
        else:
            models_index.append([model.id, len(models_index) + 1])

            # Переписывам индекс с новой парой
            with open(self.models_index_path, "w") as f:
                models_index = sorted(models_index)
                json.dump(models_index, f)

            # Записываем информацию о модели в файл
            model_json = model.model_dump_json().ljust(500) + '\n'
            with open(self.models_data_path, "a") as f:
                f.write(model_json)

        return model

    # Задание 1. Сохранение автомобилей
    def add_car(self, car: Car) -> Car:

        # Читам файл с индексами 
        with open(self.cars_index_path, "r") as f:
            try:
                cars_index = json.load(f)
            except json.JSONDecodeError:
                cars_index = []

        # Проверяем, есть ли уже такой vin в индексе
        for index in cars_index:
            if index[0] == car.vin:
                break
        # Если такого нет, добавляем пару "vin - номер строки"
        else:
            cars_index.append([car.vin, len(cars_index) + 1])

            # Переписывам индекс с новой парой
            with open(self.cars_index_path, "w") as f:
                cars_index = sorted(cars_index)
                json.dump(cars_index, f)

            # Записываем информацию о машине в файл
            car_json = car.model_dump_json().ljust(500) + '\n'
            with open(self.cars_data_path, "a") as f:
                f.write(car_json)

        return car
    
    # Найти машину по vin
    def find_car(self, vin: str) -> Car:

        # Читаем файл с индексами
        cars_index = self.read_index(self.cars_index_path)

        # По vin ищем номер строки
        for index in cars_index:
            if index[0] == vin:
                line_number = index[1] - 1
                print(line_number)
                break

        # По номеру строки ищем данные о машине в файле
        with open(self.cars_data_path, "r") as f:
            f.seek(line_number * (501))
            val = f.read(500).rstrip()

        car_json = json.loads(val)

        return Car(
            vin=str(car_json["vin"]),
            model=int(car_json["model"]),
            price=Decimal(car_json["price"]),
            date_start=datetime.fromisoformat(car_json["date_start"]),
            status=CarStatus(car_json["status"])
            )

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:

        # Читаем файл с индексами
        sales_index = self.read_index(self.sales_index_path)

        # Проверяем, есть ли уже такой номер продажи в индексе
        for index in sales_index:
            if index[0] == sale.sales_number:
                break
        # Если такого нет, добавляем пару "номер продажи - номер строки"
        else:
            sales_index.append([sale.sales_number, len(sales_index) + 1])

            # Переписывам индекс с новой парой
            with open(self.sales_index_path, "w") as f:
                sales_index = sorted(sales_index)
                json.dump(sales_index, f)

            # Записываем информацию о продаже в файл
            sale_json = sale.model_dump_json().ljust(500) + '\n'
            with open(self.sales_data_path, "a") as f:
                f.write(sale_json)

        return None

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        raise NotImplementedError

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        raise NotImplementedError

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        raise NotImplementedError

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        raise NotImplementedError

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        raise NotImplementedError


if __name__ == "__main__":
    car_service = CarService('bibip_database')

    print(car_service.find_car('5XYPH4A10GG021831'))