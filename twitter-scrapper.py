import argparse
import configparser
import logging
import os
from datetime import datetime

import jsonlines
import tweepy

import models

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def parse_args(config):
    parser = argparse.ArgumentParser(description='Extract tweets')
    available_countries = list(config['LOCATION'].keys())
    parser.add_argument('--location', metavar='Location', type=str, help='Predefined location', required=True,
                        choices=available_countries, dest='location')
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


args = parse_args(config)
location_name = args.location
geocode = config['LOCATION'][location_name]

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
cursor = tweepy\
    .Cursor(api.search, q=search_query, lang=language, count=count, since=since, geocode=geocode,
            tweet_mode="extended")\
    .items(count)

out_dir = './results'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

output_location = out_dir + "/" + "tweets-" + location_name + "-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
output_file_handler = open(output_location, "w")
lines_writer = jsonlines.Writer(output_file_handler, flush=True)
count_tweets = 1

for tweet in cursor:
    if hasattr(tweet, 'retweeted_status'):
        continue

    tweet = models.to_dataclass_tweet(tweet)
    author_screen_name = tweet.author.screen_name
    tweet_id = tweet.id
    query_replies = "to:{}".format(author_screen_name)

    logging.info("Tweet {}: {}".format(count_tweets, tweet.text))
    count_tweets += 1

    cursor_replies = tweepy\
        .Cursor(api.search, lang=language, q=query_replies, since_id=tweet_id, result_type='recent',
                tweet_mode="extended")\
        .items(count_replies)

    tweet_as_dict = models.dataclass_to_dict(tweet)

    replies = []
    for reply in cursor_replies:
        if hasattr(reply, 'in_reply_to_status_id_str') and reply.in_reply_to_status_id_str == tweet.id_str:
            reply = models.to_dataclass_tweet(reply)
            reply_as_dict = models.dataclass_to_dict(reply)
            replies.append(reply_as_dict)
            logging.info("Reply to tweet: {}".format(reply.text))

    if len(replies) > 0:
        tweet_as_dict['responses'] = replies

    lines_writer.write(tweet_as_dict)

lines_writer.close()
output_file_handler.close()






