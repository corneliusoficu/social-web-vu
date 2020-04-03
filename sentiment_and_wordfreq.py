import os
import sys

import pandas as pd
import nltk
import jsonlines
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

vader_model = SentimentIntensityAnalyzer()


def VADER_sentiment(data):
    #use VADER to get sentiment scores -> https://github.com/cjhutto/vaderSentiment for thresholds and more info
    #return dataframe with all information + column with sentiment
    
    #open as pd dataframe 
    #df = pd.read_json(data, lines=True) 
    with jsonlines.open(data) as reader:
        df = pd.DataFrame(data=reader)
     
    #add sentiment score -> the data has to be in English, sooo I don't knowwww how to change it to russian and shit
    sentiment = []
    tweets_sentiments = {
        'positive': 0,
        'negative': 0,
        'neutral': 0
    }

    for tweet in df['text']:
        VADER_score = vader_model.polarity_scores(tweet)

        for key, value in VADER_score.items():
            if key == 'compound':
                if value >= 0.05:
                    sentiment.append('positive')
                    tweets_sentiments['positive'] += 1
                if value <= -0.05:
                    sentiment.append('negative')
                    tweets_sentiments['negative'] += 1
                if -0.05 < value < 0.05:
                    sentiment.append('neutral')
                    tweets_sentiments['neutral'] += 1

    total = tweets_sentiments['positive'] + tweets_sentiments['negative'] + tweets_sentiments['neutral']
    perc_positive = tweets_sentiments['positive'] / total * 100
    perc_negative = tweets_sentiments['negative'] / total * 100
    perc_neutral = tweets_sentiments['neutral'] / total * 100
    print("Positive: {}% | Negative: {}% | Neutral: {}%".format(perc_positive, perc_negative, perc_neutral))
    return (df)


def word_frequencies_nouns(df):
    #get frequencies of words in relation to sentiment
    #return dataframe with rows of words and columns of pos - neg - neutral - total
    
    word_freq_dict = {}
    for i in range(len(df)):
        #tokenize tweet and tag the words
        tokenized_tweet = nltk.word_tokenize(df['text'][i])
        tagged_tweets = nltk.pos_tag(tokenized_tweet)

        for word, tag in tagged_tweets:
            #only take nouns
            if tag == 'NN':
                if word not in word_freq_dict:
                    word_freq_dict[word] = 0
                word_freq_dict[word] += 1

    word_freq_dict = {k: v for k, v in sorted(word_freq_dict.items(), key=lambda item: item[1], reverse=True)}


if __name__ == '__main__':
    df_with_sentiment = VADER_sentiment('results/tweets-canada-2020-03-14_19:36:20')
    word_frequencies_nouns(df_with_sentiment)