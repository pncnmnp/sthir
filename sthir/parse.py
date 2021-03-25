from typing import List

from bs4 import BeautifulSoup
from newspaper import Article
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer, word_tokenize


def extract_html_bs4(html_file_path: str,
                     remove_stopwords: bool = True,
                     enable_lemmetization: bool = False):
    """
    Given a path to html file it will extract all text in it and return a list of words
    (using library: BeautifulSoup4)

    :param html_file_path: Path to html file, will be called with open()
    :type html_file_path: str
    :param remove_stopwords: Will remove stopwords like ["the", "them",etc], defaults to False
    :type remove_stopwords: bool, optional
    :param enable_lemmetization: Will lemmetize words if set to True. Ex: cats->cat, defaults to False
    :type enable_lemmetization: bool, optional
    :return: A list of words all in lowercase
    :rtype: List[str]
    """
    # Following: https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    # By PeYoTlL
    invalid_words = set(stopwords.words("english") + ['', ""])

    with open(html_file_path, encoding='utf8') as html_file:
        soup = BeautifulSoup(html_file, features="lxml")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    # Extracting lines
    lines = [line.strip() for line in text.splitlines()]

    # Tokenizing words
    tokenizer = RegexpTokenizer(r'\w+')

    # Flatten
    chunks = []
    for line in lines:
        chunks.extend(tokenizer.tokenize(line.lower()))

    # Remove stopwords
    if remove_stopwords:
        chunks = [chunk for chunk in chunks if chunk not in invalid_words]

    #Lemmatization
    if enable_lemmetization:
        lemmatizer = WordNetLemmatizer()
        chunks = [lemmatizer.lemmatize(chunk) for chunk in chunks]

    return chunks


def extract_html_newspaper(html_file: str,
                           remove_stopwords=True,
                           enable_lemmetization=False) -> List[str]:
    """
    Given a path to html file it will extract all text in it and return a list of words
    (using library: Newspaper3k)

    :param html_file_path: Path to html file, will be called with open()
    :type html_file_path: str
    :param remove_stopwords: Will remove stopwords like ["the", "them",etc], defaults to False
    :type remove_stopwords: bool, optional
    :return: A list of words all in lowercase
    :rtype: List[str]
    """
    invalid_words = set(stopwords.words("english"))

    article = Article(url="")
    # with open(html_file_path, encoding='utf8') as html_file:
    article.set_html(open(html_file, "r", encoding='utf8').read())
    article.parse()
    text = article.text

    lines = word_tokenize(text)
    lines = [line.strip() for line in lines]

    # Tokenizing words
    tokenizer = RegexpTokenizer(r'\w+')

    # Flatten
    chunks = []
    for line in lines:
        chunks.extend(tokenizer.tokenize(line.lower()))

    # Remove stopwords
    if remove_stopwords:
        chunks = [chunk for chunk in chunks if chunk not in invalid_words]

    #Lemmatization
    if enable_lemmetization:
        lemmatizer = WordNetLemmatizer()
        chunks = [lemmatizer.lemmatize(chunk) for chunk in chunks]

    return chunks


if __name__ == "__main__":
    import time

    import requests
    start = time.time()
    response = requests.get("https://endler.dev/2018/ls/")
    print("Fetched URL in {} seconds.".format(time.time() - start))
    print(extract_html_newspaper(response.text))
