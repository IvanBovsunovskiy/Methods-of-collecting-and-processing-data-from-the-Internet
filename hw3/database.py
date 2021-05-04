import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models


class SQLDatabase:
    def __init__(self, url):
        self.engine = create_engine(url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def _get_or_create(self, session, model, filter_field, **kwargs):
        instance = session.query(model).filter_by(**{filter_field: kwargs[filter_field]}).first()
        if not instance:
            instance = model(**kwargs)
        return instance

    def add_post(self, data):
        session = self.maker()
        post = self._get_or_create(session, models.Post, "id", **data["post_data"])
        author = self._get_or_create(session, models.Author, "url", **data["author_data"])
        tags = map(
            lambda tag_data: self._get_or_create(session, models.Tag, "name", **tag_data),
            data["tags_data"],
        )
        comments = map(
            lambda comment_data: self._get_or_create(session, models.Comment, "id", **comment_data),
            data["comments"],
        )
        post.author = author
        post.tags.extend(tags)
        post.comments.extend(comments)

        print(data)
        print(author)
        for itm in post.tags:
            itm.posts.append(post)
        for itm in post.comments:
            if itm.parent_id:
                itm.parent = session.query(models.Comment).filter_by(id=itm.parent_id).first()
        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
        finally:
            session.close()
