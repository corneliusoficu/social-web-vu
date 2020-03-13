import argparse
import configparser
import os

import tweepy

import models
import json

from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description='Extract tweets')
    parser.add_argument('--location', metavar='Location', type=str, help='Predefined location', required=True,
                        choices=["Egypt", "Russia", "SaudiArabia"], dest='location')
    return parser.parse_args()


config = configparser.ConfigParser()
config.read('config.ini')
search_query = config['SCRAPER']['Query']
language = config['SCRAPER']['Language']
count = int(config['SCRAPER']['Count'])
count_replies = int(config['SCRAPER']['CountReplies'])
since = config['SCRAPER']['Since']

secrets_config = configparser.ConfigParser()
secrets_config.read('secrets.ini')
consumer_key = secrets_config['TWITTER']['ConsumerApiKey']
consumer_secret = secrets_config['TWITTER']['ConsumerApiSecretKey']
access_token = secrets_config['TWITTER']['AccessToken']
access_token_secret = secrets_config['TWITTER']['AccessTokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

args = parse_args()
location_name = args.location
geocode = config['LOCATION'][location_name]

api = tweepy.API(auth, wait_on_rate_limit=True)
cursor = tweepy\
    .Cursor(api.search, q=search_query, lang=language, count=count, since=since, geocode=geocode)\
    .items(count)

tweets = {
    'tweets': [],
    'count': 0
}

for tweet in cursor:
    if hasattr(tweet, 'retweeted_status'):
        continue
    tweet = models.to_dataclass_tweet(tweet)
    author_screen_name = tweet.author.screen_name
    tweet_id = tweet.id
    query_replies = "to:{}".format(author_screen_name)

    print("Tweet: {}".format(tweet.text))

    cursor_replies = tweepy\
        .Cursor(api.search, lang=language, q=query_replies, since_id=tweet_id, result_type='recent')\
        .items(count_replies)

    tweet_as_dict = models.dataclass_to_dict(tweet)

    replies = []
    for reply in cursor_replies:
        if hasattr(reply, 'in_reply_to_status_id_str') and reply.in_reply_to_status_id_str == tweet.id_str:
            reply = models.to_dataclass_tweet(reply)
            reply_as_dict = models.dataclass_to_dict(reply)
            replies.append(reply_as_dict)
            print("Reply to tweet: {}".format(reply.text))

    if len(replies) > 0:
        tweet_as_dict['responses'] = replies

    tweets['tweets'].append(tweet_as_dict)
    tweets['count'] += 1

out_dir = './results'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

output_location = out_dir + "/" + "tweets-" + location_name + "-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

with open(output_location, "w", encoding='utf8') as f:
    f.write(json.dumps(tweets, indent=4, ensure_ascii=False))







