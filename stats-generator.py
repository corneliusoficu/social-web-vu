import argparse
import json
import os

import nltk
import jsonlines
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')


vader_model = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))


def parse_args():
    parser = argparse.ArgumentParser(description='Generate statistics')
    parser.add_argument('--file', metavar='file', type=str, help='file location', required=True, dest='file_location')
    return parser.parse_args()


def add_tweet_words_to_word_freq_dict(tweet_text, word_freq_dict):
    tokenized_tweet = nltk.word_tokenize(tweet_text)
    tagged_tweets = nltk.pos_tag(tokenized_tweet)

    for word, tag in tagged_tweets:
        if word in stop_words:
            continue

        if word not in word_freq_dict:
            word_freq_dict[word] = 0
        word_freq_dict[word] += 1


def add_text_sentiment_to_dict(text, sentiments_text):
    VADER_score = vader_model.polarity_scores(text)
    for key, value in VADER_score.items():
        if key == 'compound':
            if value >= 0.05:
                sentiments_text['positive'] += 1
            if value <= -0.05:
                sentiments_text['negative'] += 1
            if -0.05 < value < 0.05:
                sentiments_text['neutral'] += 1


if __name__ == '__main__':
    args = parse_args()
    file_location = args.file_location
    file = open(file_location, "r")
    reader = jsonlines.Reader(file)

    word_freq = {}

    sentiments = {
        'positive': 0,
        'positive_proc': 0,
        'negative': 0,
        'negative_proc': 0,
        'neutral': 0,
        'neutral_proc': 0,
        'total': 0
    }

    for line in reader:
        tweet_text = line['text']
        add_text_sentiment_to_dict(tweet_text, sentiments)
        add_tweet_words_to_word_freq_dict(tweet_text, word_freq)

        if 'responses' in line:
            for response in line['responses']:
                add_text_sentiment_to_dict(response['text'], sentiments)
                add_tweet_words_to_word_freq_dict(response['text'], word_freq)

    sentiments['total'] = sentiments['positive'] + sentiments['negative'] + sentiments['neutral']
    sentiments['positive_proc'] = "%.4f%%" % (sentiments['positive'] / sentiments['total'] * 100)
    sentiments['negative_proc'] = "%.4f%%" % (sentiments['negative'] / sentiments['total'] * 100)
    sentiments['neutral_proc'] = "%.4f%%" % (sentiments['neutral'] / sentiments['total'] * 100)
    sorted_dict = {k: v for k, v in sorted(word_freq.items(), key=lambda item: item[1], reverse=True)}

    out_directory = "./results"
    if not os.path.exists(out_directory):
        os.mkdir(out_directory)

    output_file_word_freq = out_directory + "/" + os.path.basename(file.name) + "_word_frequency.json"
    with open(output_file_word_freq, "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(sorted_dict, indent=4, ensure_ascii=False))

    output_file_sentiments = out_directory + "/" + os.path.basename(file.name) + "_sentiments.json"
    with open(output_file_sentiments, "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(sentiments, indent=4, ensure_ascii=False))

