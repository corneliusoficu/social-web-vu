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
    for tweet in df['text']:
        VADER_score = vader_model.polarity_scores(tweet)
        for key, value in VADER_score.items():
            if key == 'compound':
                if value >= 0.05:
                    sentiment.append('positive')
                if value <= -0.05:
                    sentiment.append('negative')
                if value > -0.05 and value < 0.05:
                    sentiment.append('neutral')

    df['sentiment'] = sentiment
    return (df)


def word_frequencies_nouns(df):
    #get frequencies of words in relation to sentiment
    #return dataframe with rows of words and columns of pos - neg - neutral - total
    
    sent_dict = dict()
    for i in range(len(df)):
        #tokenize tweet and tag the words
        tokenized_tweet = nltk.word_tokenize(df['text'][i])
        tagged_tweets = nltk.pos_tag(tokenized_tweet)
        sent = df['sentiment'][i]
        
        for word, tag in tagged_tweets:
            #only take nouns
            if tag == 'NN':
                if word not in sent_dict:
                    sent_dict[word] = {'positive' : 0, 'negative' : 0, 'neutral' : 0, 'total' : 0}
                sent_dict[word][sent] += 1
                sent_dict[word]['total'] += 1
                
    df = pd.DataFrame(sent_dict).transpose()
    return (df)


def some_beautiful_plots_and_stuff(df):
    #VERY UNFINISHED hahahaha it's just some ugly barplots for fun
    most_positive = df.sort_values(['positive'], ascending=False)[:20]
    MAJESTIC = most_positive.plot.bar()
    most_negative = df.sort_values(['negative'], ascending=False)[:20]
    AMAZING = most_negative.plot.bar()


if __name__ == '__main__':
    df_with_sentiment = VADER_sentiment('results/tweets-canada-2020-03-14_19:36:20')
    word_frequencies_nouns = word_frequencies_nouns(df_with_sentiment)
    some_beautiful_plots_and_stuff(word_frequencies_nouns)