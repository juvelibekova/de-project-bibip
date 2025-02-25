from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json
from collections import Counter
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
    def read_index(self, path: Path) -> list:
        """ Чтение файла с индексом """
        with open(path, "r") as f:
            try:
                index = json.load(f)
            except json.JSONDecodeError:
                index = []

        return index

    # Обновляет файл с индексом
    def add_index(self, path: Path, index: list) -> None:
        """ Добавляет новый индекс (перезаписывает файл) """
        with open(path, "w") as f:
            index = sorted(index)
            json.dump(index, f)

        return None

    # Чтение файла с данными:
    def read_data(self, path: Path, line_number: int) -> dict:
        """ Считывает данные из файла по номеру строки """
        with open(path, "r") as f:
            f.seek(line_number * (501))
            val = f.read(500).rstrip()
        json_obj = json.loads(val)
        return json_obj

    # Записывает данные в файл
    def write_data(self, path: Path, obj, line_number: int | None) -> None:
        """ Записывает данные в файл на нужную строку"""
        if line_number is not None:
            json_obj = obj.model_dump_json().ljust(500) + '\n'
            with open(path, "r+") as f:
                f.seek(line_number * (501))
                f.write(json_obj)

    # Находит номер строки
    def find_line(self, path: Path, id) -> int | None:
        """ Находит номер строки """
        index = self.read_index(path)
        for entry in index:
            if entry[0] == id:
                return entry[1]
        return None

    # Найти машину по vin
    def find_car(self, vin: str) -> Car | None:
        """ По vin находит машину в файле с данными """
        line_number = self.find_line(self.cars_index_path, vin)
        if line_number is not None:
            json_obj = self.read_data(self.cars_data_path, line_number)
            car = Car(**json_obj)
            return car
        else:
            print(f'Данные о машине {vin} не найдены')
            return None

    # Найти модель по id
    def find_model(self, id: int) -> Model | None:
        """ По id находит модель"""
        line_number = self.find_line(self.models_index_path, id)
        if line_number is not None:
            json_obj = self.read_data(self.models_data_path, line_number)
            model = Model(**json_obj)
            return model
        print(f'Данные о модели "{id}" не найдены')
        return None

    # Найти продажу но номеру
    def find_sale(self, sales_number):
        """ По номеру продажи находит данные о продаже """
        line_number = self.find_line(self.sales_index_path, sales_number)
        if line_number is not None:
            json_obj = self.read_data(self.sales_data_path, line_number)
            sale = Sale(**json_obj)
            return sale
        else:
            print('Данные о продаже не найдены')
            return None

    # Обновить статус
    def update_status(self, vin: str, new_status: CarStatus) -> Car | None:
        """ Устанавливает новый статус для машины """
        car = self.find_car(vin)  # Находим машину и номер строки
        if car:
            car.status = CarStatus(new_status)  # Обновляем статус
            line_number = self.find_line(self.cars_index_path, vin)
            self.write_data(self.cars_data_path, car, line_number)
            return car
        return None

    # Задание 1. Сохранение моделей
    def add_model(self, model: Model) -> Model:
        """ Записывает в файлы информацию о новой модели """
        # Читаем файл с индексами
        models_index = self.read_index(self.models_index_path)

        # Проверяем, есть ли уже такой id в индексе
        for index in models_index:
            if index[0] == model.id:
                break
        else:
            line_number = len(models_index)
            models_index.append([model.id, line_number])
            self.add_index(self.models_index_path, models_index)
            self.write_data(self.models_data_path, model, line_number)

        return model

    # Задание 1. Сохранение автомобилей
    def add_car(self, car: Car) -> Car:
        """ Записывает в файлы информацию о новой машине """
        # Читаем файл с индексами
        cars_index = self.read_index(self.cars_index_path)

        # Проверяем, есть ли уже такой vin в индексе
        for index in cars_index:
            if index[0] == car.vin:
                break
        # Если такого нет, добавляем пару "vin - номер строки"
        else:
            line_number = len(cars_index)
            cars_index.append([car.vin, line_number])
            self.add_index(self.cars_index_path, cars_index)
            self.write_data(self.cars_data_path, car, line_number)

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car | None:
        """ Записывает в файлы информацию о новой продаже """
        car = self.find_car(sale.car_vin)
        if car:
            sales_index = self.read_index(self.sales_index_path)
            # Проверяем, есть ли уже такой номер продажи в индексе
            for index in sales_index:
                if index[0] == sale.sales_number:
                    break
            else:
                line_number = len(sales_index)
                sales_index.append([sale.sales_number, line_number])
                self.add_index(self.sales_index_path, sales_index)
                self.write_data(self.sales_data_path, sale, line_number)
                car = self.update_status(sale.car_vin, CarStatus.sold)
            return car
        return None

    # Задание 3 Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        """ Возвращает список машин с нужным статусом """
        cars_with_status = []
        index = self.read_index(self.cars_index_path)

        for i in range(len(index)):
            car_json = self.read_data(self.cars_data_path, i)
            if car_json["status"] == status:
                car = Car(**car_json)  # Из json в объект класса.
                cars_with_status.append(car)

        return cars_with_status

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """ Собирает детальную информацию машина-модель-продажа """
        car = self.find_car(vin)
        if not car:
            return None  # Если нет машины - None.

        model = self.find_model(car.model)
        if not model:
            return None  # Если нет модели - None.

        sd, sc = None, None
        if car.status == 'sold':
            index = self.read_index(self.sales_index_path)
            for entry in index:
                sale_json = self.read_data(self.sales_data_path, entry[1])
                if sale_json["car_vin"] == car.vin:
                    sale = Sale(**sale_json)  # Из json в объект класса.
                    sd = sale.sales_date
                    sc = sale.cost
                    break

        return CarFullInfo(
            vin=car.vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=Decimal(car.price),
            date_start=car.date_start,
            status=car.status,
            sales_date=sd,
            sales_cost=sc
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car | None:
        """ Обновляет vin в записи машины  и перезаписывает новый индекс """
        car = self.find_car(vin)
        line_number = self.find_line(self.cars_index_path, vin)
        # перезаписали в файл новый vin
        if car:
            car.vin = new_vin
            self.write_data(self.cars_data_path, car, line_number)
            index = self.read_index(self.cars_index_path)
            # переписываем индекс
            for entry in index:
                if entry[0] == vin:
                    entry[0] = new_vin
            # записываем новый индекс в файл
            self.add_index(self.cars_index_path, index)
            return car
        return None

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car | None:
        """ Удаляет данные о продаже"""
        sale = self.find_sale(sales_number)  # Находим продажу
        car = self.update_status(sale.car_vin, CarStatus.available)
        if car:
            index = self.read_index(self.sales_index_path)  # Читаем индекс
            # Удаляем индекс
            for i in range(len(index)):
                if index[i][0] == sales_number:
                    index.pop(i)
                    break
            self.add_index(self.sales_index_path, index)  # Переписываем индекс
            return car
        return None

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats] | None:
        """ Возвращает список трех самых продаваемых моделей машин """
        cars = self.get_cars(CarStatus.sold)
        price_model = sorted(
            [(car.price, car.model) for car in cars], reverse=True
        )
        sorted_models = [model for _, model in price_model]
        top3_models = Counter(sorted_models).most_common(3)

        top3_models_data = []
        for mdl in top3_models:
            model = self.find_model(mdl[0])
            if not model:
                return None

            model_stat = ModelSaleStats(
                car_model_name=model.name,
                brand=model.brand,
                sales_number=mdl[1]
            )
            top3_models_data.append(model_stat)

        return top3_models_data


models = [
    Model(
        id=1,
        name='Optima',
        brand='Kia'
    ),
    Model(
        id=2,
        name='Sorento',
        brand='Kia'
    ),
    Model(
        id=3,
        name='3',
        brand='Mazda'
    ),
    Model(
        id=4,
        name='Pathfinder',
        brand='Nissan'
    ),
    Model(
        id=4,
        name='Logan',
        brand='Renault'
    )
]

cars = [
    Car(
        vin="KNAGM4A77D5316538",
        model=1,
        price=Decimal("2000"),
        date_start=datetime(2024, 2, 8),
        status=CarStatus.available,
    ),
    Car(
        vin="5XYPH4A10GG021831",
        model=2,
        price=Decimal("2300"),
        date_start=datetime(2024, 2, 20),
        status=CarStatus.reserve,
    ),
    Car(
        vin="KNAGH4A48A5414970",
        model=1,
        price=Decimal("2100"),
        date_start=datetime(2024, 4, 4),
        status=CarStatus.available,
    ),
    Car(
        vin="JM1BL1TFXD1734246",
        model=3,
        price=Decimal("2276.65"),
        date_start=datetime(2024, 5, 17),
        status=CarStatus.available,
    ),
    Car(
        vin="JM1BL1M58C1614725",
        model=3,
        price=Decimal("2549.10"),
        date_start=datetime(2024, 5, 17),
        status=CarStatus.reserve,
    ),
    Car(
        vin="KNAGR4A63D5359556",
        model=1,
        price=Decimal("2376"),
        date_start=datetime(2024, 5, 17),
        status=CarStatus.available,
    ),
    Car(
        vin="5N1CR2MN9EC641864",
        model=4,
        price=Decimal("3100"),
        date_start=datetime(2024, 6, 1),
        status=CarStatus.available,
    ),
    Car(
        vin="JM1BL1L83C1660152",
        model=3,
        price=Decimal("2635.17"),
        date_start=datetime(2024, 6, 1),
        status=CarStatus.available,
    ),
    Car(
        vin="5N1CR2TS0HW037674",
        model=4,
        price=Decimal("3100"),
        date_start=datetime(2024, 6, 1),
        status=CarStatus.available,
    ),
    Car(
        vin="5N1AR2MM4DC605884",
        model=4,
        price=Decimal("3200"),
        date_start=datetime(2024, 7, 15),
        status=CarStatus.available,
    ),
    Car(
        vin="VF1LZL2T4BC242298",
        model=5,
        price=Decimal("2280.76"),
        date_start=datetime(2024, 8, 31),
        status=CarStatus.delivery,
    )
]

sales = [
    Sale(
        sales_number="20240903#KNAGM4A77D5316538",
        car_vin="KNAGM4A77D5316538",
        sales_date=datetime(2024, 9, 3),
        cost=Decimal("1999.09"),
    ),
    Sale(
        sales_number="20240903#KNAGH4A48A5414970",
        car_vin="KNAGH4A48A5414970",
        sales_date=datetime(2024, 9, 4),
        cost=Decimal("2100"),
    ),
    Sale(
        sales_number="20240903#KNAGR4A63D5359556",
        car_vin="KNAGR4A63D5359556",
        sales_date=datetime(2024, 9, 5),
        cost=Decimal("7623"),
    ),
    Sale(
        sales_number="20240903#JM1BL1M58C1614725",
        car_vin="JM1BL1M58C1614725",
        sales_date=datetime(2024, 9, 6),
        cost=Decimal("2334"),
    ),
    Sale(
        sales_number="20240903#JM1BL1L83C1660152",
        car_vin="JM1BL1L83C1660152",
        sales_date=datetime(2024, 9, 7),
        cost=Decimal("451"),
    ),
    Sale(
        sales_number="20240903#5N1CR2TS0HW037674",
        car_vin="5N1CR2TS0HW037674",
        sales_date=datetime(2024, 9, 8),
        cost=Decimal("9876"),
    ),
    Sale(
        sales_number="20240903#5XYPH4A10GG021831",
        car_vin="5XYPH4A10GG021831",
        sales_date=datetime(2024, 9, 9),
        cost=Decimal("1234"),
    )
]

if __name__ == "__main__":
    car_service = CarService('bibip_database')
    for model in models:
        car_service.add_model(model)
    for car in cars:
        car_service.add_car(car)
    for sale in sales:
        car_service.sell_car(sale)
    # print(car_service.get_cars(CarStatus.available))
    # print(car_service.get_car_info('KNAGH4A48A5414970'))
    # print(car_service.top_models_by_sales())
