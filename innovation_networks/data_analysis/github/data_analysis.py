"""GitHub data analysis as part of the innovation networks data pilot"""

import argparse
import logging
import json
import nltk
import os
import string

from gensim import corpora
from gensim import models
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from pprint import pprint


def process_words(sentence, lmtzr=None):
    """Take a string, tokenize it, remove stop words and return filtered tokens
    as a list"""
    try:
        sentence = sentence.lower()
        sentence = "".join([w for w in sentence if w not in string.punctuation])
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        if lmtzr:
            tokens = [lmtzr.lemmatize(token) for token in tokens]

        filtered_words = [token for token in tokens if token not in stopwords.words('english')]
        return filtered_words
    except AttributeError as e:
        logging.exception(e)


def main():
    """Main function run when file run from command line"""

    # log to tmp dir
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO,
                        filename='/tmp/github.data_analysis.log')

    # Sets the base directory as being innovation_networks/innovation_networks
    # and creates the output directory for results
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    OUT_DIR = os.path.join(BASE_DIR, 'data/results')
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)

    # Command line Arguments
    parser = argparse.ArgumentParser(description="Github data analysis")
    parser.add_argument(dest='datafile',
                        action='store',
                        help='path to data file')
    args = parser.parse_args()

    # create a lemmatizer object
    lmtzr = WordNetLemmatizer()

    # Load the data
    with open(args.datafile) as fp:
        data = json.load(fp)

    # Get the tokens and build corpora
    dictionary = {}
    for user in data:
        repo_description_corpus = [process_words(
            repo['description'], lmtzr=lmtzr) for repo in data[user]]

        # Create a dictionary of unique tokens
        try:
            dictionary = corpora.Dictionary(repo_description_corpus)
            corpus = [dictionary.doc2bow(doc) for doc in repo_description_corpus]

            tf_idf = models.TfidfModel(corpus)
            tf_idf_corpus = tf_idf[corpus]

            print(tf_idf_corpus)

            lda_model = models.LdaModel(tf_idf_corpus,
                                        id2word=dictionary,
                                        num_topics=5,
                                        passes=10,
                                        iterations=150)

            #pprint(lda_model.show_topics(num_topics=5))
        except TypeError as e:
            logging.exception(e)


if __name__ == "__main__":
    main()
