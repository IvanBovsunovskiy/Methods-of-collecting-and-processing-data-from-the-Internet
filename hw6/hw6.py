"""
Источник https://www.avito.ru/krasnodar/kvartiry/prodam
Город можно сменить
задача обойти пагинацию и подразделы квартир в продаже.
Собрать данные:
URL
Title
Цена
Адрес (если доступен)
Параметры квартиры (блок под фото)
Ссылку на автора
Дополнительно но не обязательно вытащить телефон автора
"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from avito_real_estate.spiders.avito_real_estate import AvitoRealEstateSpider
# to prepare proxy list use proxy_list_preparation from avito_real_estate before


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("avito_real_estate.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AvitoRealEstateSpider)
    crawler_process.start()
