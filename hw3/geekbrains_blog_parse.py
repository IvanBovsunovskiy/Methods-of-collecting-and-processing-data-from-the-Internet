"""
Продолжить работу с парсером блога GB
Реализовать SQL базу данных посредствам SQLAlchemy
Реализовать реалиционные связи между Постом и Автором, Постом и Тегом, Постом и комментарием, Комментарием и комментарием
"""

import requests
from hw3.database import SQLDatabase
import time
import datetime
import typing
from bs4 import BeautifulSoup as BSoup
from urllib.parse import urljoin

class BaseParser:
    def __init__(self, start_url, *args, **kwargs):
        self.time = datetime.datetime.now().time()
        self.start_url = start_url

    def _get_response(self, url: str = None, *args, **kwargs):
        if url is None:
            url = self.star_url
        temp = 0
        check = 5
        while temp < check:
            response = requests.get(url, *args, **kwargs)
            time.sleep(0.5)
            if response.status_code == 200:
                print(url)
                return response
            temp += 1

    def _get_soup(self, url, *args, **kwargs):
        soup = BSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

class ParseGB(BaseParser):

    def __init__(self, start_url: str, collection):
        super().__init__(start_url)
        self.collection = collection
        self.done_urls = set()  # множество проверенных ссылок
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

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
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_comments(self, commentable_id):
        # https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id=2574&order=desc
        url_comments = "https://gb.ru/api/v2/comments?commentable_type=Post&order=desc&commentable_id=" \
                       + commentable_id + "&order=desc"
        comments = []
        try:
            sub_comments = self._get_response(url_comments).json()
        except AttributeError:
            sub_comments = False
        if sub_comments:
            for item in sub_comments:
                print(item)
                print(type(item))
                if type(item) == 'list':
                    if item[0]["comment"]["children"]:
                        sub_comments.append(item["comment"]["children"])
                elif type(item) == 'dict':
                    if item["comment"]["children"]:
                        sub_comments.append(item["comment"]["children"])

            for current_comment in sub_comments:
                print(commentable_id)
                comments.append({"id": current_comment["comment"]["id"],
                                 "post_id": commentable_id,
                                 "full_name": current_comment["comment"]["user"]["full_name"],
                                 "user_url": current_comment["comment"]["user"]["url"],
                                 "text": current_comment["comment"]["body"],
                                 "parent_id": current_comment["comment"]["parent_id"],
                                 # "root_comment_id": current_comment["comment"]["root_comment_id"],
                                 }
                                )
        else:
            comments.append({"id": 0,
                             "post_id": commentable_id,
                             "full_name": '',
                             "user_url": 'none',
                             "text": '',
                             "parent_id": 0,
                             # "root_comment_id": 0,
                             }
                            )
        return comments

    def parse_post(self, url, soup):
        # <h1 class="blogpost-title text-left text-dark m-t-sm" ng-non-bindable="" itemprop="headline">Soft skills и
        # hard skills: разбираем на примерах</h1>
        title_tag = soup.find("h1", attrs={"class": "blogpost-title"}).text
        # <div class="blogpost-content content_text content js-mediator-article"
        # ng-non-bindable="" itemprop="articleBody" content="<p>
        # <img alt=&quot;&quot; src=&quot;https://d2xzmw6cctk25h.cloudfront.net/geekbrains/public/ckeditor_assets/
        # pictures/10903/retina-9ac6be4633402ef6f4afeb76aaa486f0.png&quot;></p>
        temp_soup = soup.find("div", attrs={"class": "blogpost-content content_text content js-mediator-article"})
        # some posts have no any first images "https://gb.ru/posts/90_day_management_from_stratoplan"
        if temp_soup.find("img"):
            image_href = temp_soup.find("img").attrs.get("src")  # only first conjunction
        else:
            image_href = "https://wiki.openstreetmap.org/w/images/thumb/9/92/None_yet.svg/200px-None_yet.svg.png"
        # <div class="blogpost-date-views">
        #   <time class="text-md text-muted m-r-md" datetime="2021-04-13T15:33:26+03:00" itemprop="datePublished">
        #   13 апреля 2021</time>
        temp_soup = soup.find("div", attrs={"class": "blogpost-date-views"})
        datetime_post = temp_soup.find("time", attrs={"class": "text-md text-muted m-r-md"}).get("datetime")
        # <div class="row m-t">
        #   <div class="col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v">
        #       <a style="text-decoration:none;" href="/users/4251958" rel="nofollow">
        #           <div class="thumb avatar thumb-sm pull-left m-r">
        #               <img class="user-avatar-image" src="https://d2xzmw6cctk25h.cloudfront.net/avatar/2766516/
        #               attachment/thumb-e85efb1894cb7d3be6ba2ac7563fc506.jpeg"></div>
        #           <div class="text-lg text-dark" style="line-height:14px;" itemprop="author">Елизавета  Гаврилова</div>
        temp_soup = soup.find("div", attrs={"class": "row m-t"})
        author_href = temp_soup.find("a").get("href")
        author_name = temp_soup.find(attrs={"text-lg"}).text

        comments_table_id = soup.find("comments").attrs.get("commentable-id")
        list_comments = self.parse_comments(comments_table_id)
        data = {
            "post_data": {
                "id": soup.find("comments").attrs.get("commentable-id"),
                "title": title_tag,
                "url": url,
                "image_url": image_href,
                "date_time": datetime.datetime.fromtimestamp(int(time.mktime(time.strptime(datetime_post, "%Y-%m-%dT%X%z")))
                                                    + time.timezone)
            },
            "author_data": {
                "url": urljoin(url, author_href),
                "name": author_name,
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments": list_comments
        }
        return data

    def run(self):
        print(self.time)
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                print(datetime.datetime.now().time())
                self.save(task_result)

    def save(self, data):
        self.collection.add_post(data)


if __name__ == "__main__":
    db = SQLDatabase("sqlite:///gb_blog.db")
    parser = ParseGB("https://gb.ru/posts", db)
    parser.run()
