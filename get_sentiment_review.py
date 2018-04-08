from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import sent_tokenize
import sys
import nltk
reload(sys)
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
sys.setdefaultencoding('utf8')

tokenizer = RegexpTokenizer(r'\w+')
lemma = WordNetLemmatizer()
stemmer = PorterStemmer()
sid = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))


def get_calculated_start_value(polariy_score, compound_score):
    star_hash = {}
    if (polariy_score and compound_score == -2) or (polariy_score and compound_score == -3):
        star_hash['polarity_star_value'] = -1
        star_hash['compound_star_value'] = -1
        star_hash['averaged_star_value'] = -1
    else:
        old_min = -1
        old_max = 1
        new_min = 0
        new_max = 5
        polarity_based_star_value = (((polariy_score - old_min) * (new_max - new_min))/(old_max - old_min)) + new_min
        compound_based_star_value = (((compound_score - old_min) * (new_max - new_min))/(old_max - old_min)) + new_min
        averaged_star_value = (polarity_based_star_value + compound_based_star_value)/2
        star_hash['polarity_star_value'] = polarity_based_star_value
        star_hash['compound_star_value'] = compound_based_star_value
        star_hash['averaged_star_value'] = averaged_star_value
    return star_hash


def get_text_blob_sentiment(text):
    text = text.decode('utf-8')
    blob_data = TextBlob(text)
    polarity_list = []
    for sentence in blob_data.sentences:
        polarity_list.append(sentence.sentiment.polarity)
    return polarity_list,sum(polarity_list)/len(polarity_list)


def get_sentences(text):
    return sent_tokenize(text.decode('utf-8'))


def get_words(text):
    return tokenizer.tokenize(text.decode('utf-8'))


def get_stop_word_removed_list(review_words):
    stop_word_removed_list = []
    for word in review_words:
        word = word.lower()
        if word not in stop_words:
            stop_word_removed_list.append(word)
    return stop_word_removed_list


def get_lemmatized_words(list_of_words):
    lemmatized_word_list = []
    for word in list_of_words:
        lemmatized_word_list.append(lemma.lemmatize(word.decode('UTF-8')))
    return lemmatized_word_list


def get_stemmed_words(list_of_words):
    stemmed_word_list = []
    for word in list_of_words:
        stemmed_word_list.append(stemmer.stem(word.decode('UTF-8')))
    return stemmed_word_list


def get_nltk_compound(sentences):
    nltk_polarity = []
    for sentence in sentences:
        ss = sid.polarity_scores(sentence)
        nltk_polarity.append(ss['compound'])
    return nltk_polarity, sum(nltk_polarity) / len(nltk_polarity)


def get_sentiment_values(review):
    response_hash = {}
    response_hash['review_sentences'] = get_sentences(review)
    response_hash['review_words'] = get_words(review)
    response_hash['stop_word_removed'] = get_stop_word_removed_list(response_hash['review_words'])
    response_hash['stemmed_words'] = get_stemmed_words(response_hash['stop_word_removed'])
    # response_hash['lemmatized_words'] = get_lemmatized_words(response_hash['stop_word_removed'])
    response_hash['text_blob_polarity_list'], response_hash['text_blob_polarity'] = get_text_blob_sentiment(review)
    response_hash['nltk_polarity_list'], response_hash['nltk_polarity_score'] = get_nltk_compound(response_hash['review_sentences'])
    response_hash['stars'] = get_calculated_start_value(response_hash['text_blob_polarity'],response_hash['nltk_polarity_score'])
    return response_hash