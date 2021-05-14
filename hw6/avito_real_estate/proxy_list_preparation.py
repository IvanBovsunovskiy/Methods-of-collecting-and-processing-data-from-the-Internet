from bs4 import BeautifulSoup
import time
import typing
import requests
from urllib.parse import urljoin
from subprocess import Popen, PIPE
import re


class ProxyParse:
    def __init__(self, start_url, proxies_list_length):
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0'
                        }
        self.proxies_list_length = proxies_list_length
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)
        self.proxy_list = []

    def _get_response(self, url, *args, **kwargs):
        time.sleep(0.5)
        response = requests.get(url, headers=self.headers, *args, **kwargs)
        print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href")) for itm in tags_list if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("div", class_={"pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        self.proxy_list.extend(self.parse_proxy(soup))

    def parse_proxy(self, soup):
        proxy_soup = soup.find("div", class_={"table_block"})
        proxy_soup = proxy_soup.find('tbody')
        proxy_list = []
        for incident in proxy_soup('tr'):
            single_proxy, _, _, ping_time = incident.contents[:4]
            single_proxy = single_proxy.getText()
            ping_time = ping_time.getText()[:-3]
            if int(ping_time) < 200:
                try:
                    ping_text = f'ping -c 3 {single_proxy}'  # обеспечивает суммарный выход 3 пингов без отдельных пингов печати
                    cmd = Popen(ping_text.split(' '), stdout=PIPE)
                    ping_request = cmd.communicate()[0].decode('utf-8')
                    ping_request_str = re.search('\d+\.+\d+\/\d+\.+\d+\/+\d+\.+\d+\s+ms', ping_request)
                    ping_request_str = ping_request_str.group()
                    ping_request_str = re.search('\d+\.+\d+', ping_request_str)
                    delay = ping_request_str.group()
                    if (not (delay is None)) & (float(delay) < 100):
                        proxy_list.append(single_proxy)
                except:
                    print('Bad server')
        return proxy_list

    def run(self):
        for task in self.tasks:
            task_result = task()
            print(len(self.proxy_list))
            if len(self.proxy_list) < self.proxies_list_length:
                print(len(self.proxy_list))
            else:
                return lambda *_, **__: None

    def save(self, data):
        self.proxy_list.append(data)


if __name__ == "__main__":
    """
    program search proxy servers with avg ping less than 200ms 
    """
    collection = []
    parser = ProxyParse("https://hidemy.name/ru/proxy-list", 10)
    parser.run()
    with open('proxies', 'a') as f:
        collection = parser.proxy_list
        collection = map(lambda x: x + '\n', collection)
        f.writelines(collection)
