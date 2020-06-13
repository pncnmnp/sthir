import newspaper
from typing import *
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def extract_html(html_file_path: str,
                 author=False,
                 title=False,
                 remove_stopwords=False) -> List[str]:
    """
    Given a path to html, file it will extract all text in it and return a list of words

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
    with open(html_file_path) as html_file:
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
