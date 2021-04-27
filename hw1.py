"""
Источник: https://5ka.ru/special_offers/
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в
Json файлы, для каждой категории товаров должен быть создан отдельный файл и содержать
товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера
{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import json
import requests
import time
from pathlib import Path


class BaseParser:
    headers = {"User-Agent": "Mozilla/5.0 Gecko/20100101 Firefox/88.0"}
    params = {}

    def __init__(self, start_url: str, categories_url: str = "https://5ka.ru/api/v2/categories/", dir: str = 'Response', cookies: str = '1843'):
        self.star_url = start_url
        self.categories_url = categories_url
        self.save_path = self._get_save_path(dir)
        self.cookies = {'location_id': cookies}

    def _get_response(self, url: str = None, *args, **kwargs):
        if url is None:
            url = self.star_url

        temp = 0
        check = 5
        while temp < check:
            response = requests.get(url, *args, **kwargs)  # timeout=(3, 10) unstable бывают задержки более 5-20 сек
            if response.status_code == 200:
                return response
            time.sleep(0.05)
            temp += 1

    def _save(self, data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def _get_save_path(self, dir_name):
        save_path = Path(__file__).parent.joinpath(dir_name)
        if not save_path.exists():
            save_path.mkdir()
        return save_path


class ParseX5(BaseParser):

    def __init__(self, start_url: str, categories_url: str, dir: str='HW1', cookies: str='1843'):  # 1843 - Saint-Petersburg
        super().__init__(start_url, categories_url, dir, cookies)

    def _parse_categories(self):
        response = self._get_response(self.categories_url, headers=self.headers, cookies=self.cookies)
        return response.json()

    def _parse_products(self, url):
        page = 1
        self.params['page'] = str(page)
        while page:
            time.sleep(0.05)
            print(f'Category number: {self.params.get("categories")}, '
                  f'Category name: {self.params.get("category_name")}, page: {page}\n')
            response = self._get_response(url, headers=self.headers, params=self.params, cookies=self.cookies)
            data = response.json()
            if data["next"] is not None:
                page += 1
                self.params['page'] = str(page)
            else:
                page = 0

            for product in data["results"]:
                yield product

    def run(self):
        cat_dict = {}
        categories = self._parse_categories()
        for cat in categories:
            cat_dict['name'] = cat['parent_group_name']
            cat_dict['code'] = cat['parent_group_code']
            cat_dict['products'] = []
            self.params['category_name'] = cat_dict['name']
            self.params['categories'] = cat_dict['code']

            for product in self._parse_products(self.star_url):
                cat_dict['products'].append(product)

            if len(cat_dict['products']) > 0:
                cat_file = self.save_path.joinpath(f"{cat_dict['name']}.json")
                self._save(cat_dict, cat_file)


if __name__ == "__main__":
    dir = "HW1_X5_5_categories"
    url = "https://5ka.ru/api/v2/special_offers/"  # откуда забираем данные
    cat_url = "https://5ka.ru/api/v2/categories/"  # откуда забираем данные для списка каталога
    region = '1843'  # Archangelsk
    parser = ParseX5(url, cat_url, dir, region)
    parser.run()
