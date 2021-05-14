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
xpath_selectors = {
    "pages": '//a[@class="pagination-page"]/@href',
    "flat": '//a[@data-marker="item-title"]/@href'
}

xpath_data_selectors = {
    "title": '//h1[@class="title-info-title"]/span/text()',
    "price": '//div[class="item-view-price-content js-item-view-price-content"]//span[@itemprop="price"]/text()',
    "address": '//span[@class="item-address__string"]/text()',
    "parameters": '//div[@class="item-params"]//li//text()',
    "author": '//div[@class="item-phone-seller-info"]//div[@data-marker="seller-info/name"]/a/@href',
}