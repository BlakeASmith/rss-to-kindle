import os
from datetime import date
from pathlib import Path

import feedparser
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import _email

engine = create_engine("sqlite:///data.db")

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"
    _id = Column(String, primary_key=True)
    feed_url = Column(String)
    title = Column(String)
    content = Column(String)
    post_date = Column(String)


Base.metadata.create_all(engine)

url = 'https://www.konstantinschubert.com/feed.xml'


def get_unseen_articles(url):
    rss = feedparser.parse(url)

    session = sessionmaker(bind=engine)()

    for entry in rss.entries:
        exists = session.query(Article._id).filter_by(_id=entry.id).first()

        if exists is None:
            article = Article(
                _id=entry.id,
                feed_url=entry.link,
                title=entry.title,
                content=entry.summary,
                post_date=entry.published,
            )
            session.add(article)
            yield article

    session.commit()


digest_path = Path(f"digest-{date.today()}.html")
mobi_path = digest_path.with_suffix('.mobi')


with digest_path.open("w", encoding="utf-8") as digest:
    digest.write(f"Articles from {url}\n")
    some_articles = False

    for _article in get_unseen_articles(url):
        some_articles = True
        digest.write(f"<h2>{_article.title}</h2>\n")
        digest.write(f"Posted on {_article.post_date}\n")
        digest.write("\n")
        digest.write(_article.content)
        digest.write("\n")

if some_articles:
    os.system(
        f"ebook-convert {digest_path} {mobi_path}"
    )

    _email.send_mail(
        from_address=os.getenv("EMAIL"),
        password=os.getenv("EMAIL_PASSWORD"),
        to_address="blake.anthony.smith_pVKcqQ@kindle.com",
        subject=f"{digest_path.name}",
        body=f"Your RSS digest for {date.today()}.",
        html_attach=mobi_path,
    )

digest_path.unlink()
mobi_path.unlink()

