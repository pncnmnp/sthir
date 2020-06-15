import newspaper
from typing import *
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer 


import urllib
from bs4 import BeautifulSoup


def extract_html_bs4(html_file_path: str, remove_stopwords: bool = True,enable_lemmetization:bool=False):
    """
    Given a path to html file it will extract all text in it and return a list of words
    (using library: BeautifulSoup4)

    :param html_file_path: Path to html file, will be called with open()
    :type html_file_path: str
    :param remove_stopwords: Will remove stopwords like ["the", "them",etc], defaults to False
    :type remove_stopwords: bool, optional
    :return: A list of words all in lowercase
    :rtype: List[str]
    """
    # Following: https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    # By PeYoTlL
    not_allowed_chars = set(string.punctuation)
    invalid_words = set(stopwords.words("english") + ['', ""])

    with open(html_file_path , encoding='utf8') as html_file:
        soup = BeautifulSoup(html_file, features="lxml")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    # Extracting lines
    lines = [line.strip() for line in text.splitlines()]

    # Tokenizing words
    tokenizer = RegexpTokenizer(r'\w+')
    chunks = [tokenizer.tokenize(line.lower()) for line in lines]

    # Flatten
    chunks = sum(chunks, [])

    # Remove stopwords
    if remove_stopwords:
        chunks = [
            chunk for chunk in chunks if chunk not in list(invalid_words)
        ]

    #Lemmatization   
    if enable_lemmetization:
        lemmatizer = WordNetLemmatizer() 
        chunks = [ lemmatizer.lemmatize(chunk) for chunk in chunks ]

    return chunks


def extract_html_newspaper(html_file_path: str,
                           author=False,
                           title=False,
                           remove_stopwords=True) -> List[str]:
    """
    Given a path to html file it will extract all text in it and return a list of words
    (using library: Newspaper3k)

    :param html_file_path: Path to html file, will be called with open()
    :type html_file_path: str
    :param author: If true, words will also contain author names, defaults to False
    :type author: bool, optional
    :param title: If true, words will also contain title, defaults to False
    :type title: bool, optional
    :param remove_stopwords: Will remove stopwords like ["the", "them",etc], defaults to False
    :type remove_stopwords: bool, optional
    :return: A list of words all in lowercase
    :rtype: List[str]
    """
    allowed_chars = set(string.ascii_lowercase + string.digits + " ")
    invalid_words = set(stopwords.words("english"))

    # Read html
    article = newspaper.Article(url="")
    with open(html_file_path, encoding='utf8') as html_file:
        article.set_html(html_file.read())
    article.parse()
    text = article.text

    # Extend with author
    if author: text += " ".join(article.authors)

    # Extend with title
    if title: text += article.title

    # Remove stopwords
    text = text.lower()
    if remove_stopwords:
        text = " ".join(t for t in text.split() if t not in invalid_words)

    # Remove invalid chars
    text = "".join(
        [character for character in text if character in allowed_chars])

    # Tokenize
    words = word_tokenize(text)
    return words


if __name__ == "__main__":
    FILE = r"Testing\Algorithms interviews_ theory vs. practice.html"
    print(extract_html_bs4(FILE)[:20])
