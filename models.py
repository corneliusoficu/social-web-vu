import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Author:
    id: int
    location: str
    name: str
    description: str
    followers_count: int
    friends_count: int
    created_at: datetime
    screen_name: str


@dataclass
class Tweet:
    id: int
    id_str: str
    text: str
    source: str
    created_at: datetime
    author: Author
    favorite_count: int
    retweet_count: int
    link: str


def to_dataclass_tweet(tweet):
    tweet_author = tweet.author
    author = Author(
        id=tweet_author.id,
        location=tweet_author.location,
        name=tweet_author.name,
        description=tweet_author.description,
        followers_count=tweet_author.followers_count,
        friends_count=tweet_author.friends_count,
        created_at=tweet_author.created_at,
        screen_name=tweet_author.screen_name)

    link = "http://twitter.com/{}/status/{}".format(tweet.author.screen_name, tweet.id)

    tweet = Tweet(
        id=tweet.id,
        id_str=tweet.id_str,
        text=tweet.text,
        source=tweet.source,
        created_at=tweet.created_at,
        author=author,
        favorite_count=tweet.favorite_count,
        link=link,
        retweet_count=tweet.retweet_count
    )

    return tweet


def clean_empty(d):
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d, %H:%M:%S")
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}


def dataclass_to_dict(obj):
    service_discovery_dict = dataclasses.asdict(obj)
    cleaned_dict = clean_empty(service_discovery_dict)
    return cleaned_dict


