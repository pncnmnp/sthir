import json
import time
from functools import partial
from math import log
import os

import lxml.html
import requests
from typing import List

import sthir.convert_2p15 as convert_2p15
import sthir.parse as parse
import sthir.spectral_bloom_filter as spectral_bloom_filter
from sthir.generate_search import base2p15_encode


def get_all_html_files(directory: str) -> List[str]:
    """
    Returns list of html files located in the directory
    """
    files = [ f for f in os.listdir(directory) if f.endswith('.html')]

    if len(files) == 0:
        raise AssertionError("The directory: {} has no HTML files.".format(directory))
    return files

def generate_bloom_filter(file: str,
                          false_positive: float = 0.1,
                          chunk_size: int = 4,
                          remove_stopwords: bool = True,
                          tokens: List = []) -> dict:
    """
    |  Generates a bloom filter and saves it in .bin file.
    |  The saved .bin filename is same as that of the .html file name.
    |  Returns a dictionary containing the - 
    |  length of the bitarray (m), no of hash functions used (k), chunk size (chunk_size), binary file name (bin_file), and HTML file's title (title).

    This method is internally used in method - create_search_page
    """
    spectral = spectral_bloom_filter.Spectral_Bloom_Filter()
    if len(tokens) == 0:
        tokens = parse.extract_html_newspaper(file,
                                          remove_stopwords=remove_stopwords)

    title = lxml.html.parse(file).find(".//title").text

    sbf = spectral.create_filter(
        tokens=tokens,
        chunk_size=chunk_size,
        p=false_positive,
    )
    m, n = len(sbf), len(tokens)
    k = round((m / n) * log(2))  # From spectral_bloom_filter.optimal_m_k
    return {
        "m": m,
        "k": k,
        "chunk_size": chunk_size,
        "sbf": sbf,
        "title": title
    }


def process_file(file: str, 
                false_positive: float, 
                chunk_size: int, 
                remove_stopwords: bool,
                tokens: List = []) -> List:
    document = generate_bloom_filter(file, false_positive, chunk_size,
                                     remove_stopwords, tokens)
    return [base2p15_encode("".join(document["sbf"])), document["chunk_size"],
            document["m"], document["k"], file, document["title"]]

def get_all_tokens(path: str, files: str, directory: str) -> dict:
    all_tokens = json.load(open(path))
    # as keys are only filenames (without the relative paths), stripping the relative paths
    strip_files_prefix = [os.path.split(file)[-1] for file in files]
    for file_name in all_tokens.keys():
        if (file_name not in strip_files_prefix):
            raise ValueError("Filename \"{}\" as mentioned in {} is not specified in directory {}".format(file_name, path, directory))
    return all_tokens

def create_search_page(directory: str,
                       output_file: str = "search.html",
                       false_positive: float = 0.1,
                       chunk_size: int = 4,
                       remove_stopwords: bool = True,
                       tokens_path: str = None) -> None:
    """
    Generates the search output file using the directory path.

    :param directory: Directory path where HTML files are located
    :param output_file: name of the output file
                        (Default - "search.html")
    :param false_positive: Acceptable false positive rate during search
                             (Default - 0.1)
                             0.01 is a better alternative, at the cost of increase in file size.
    :param chunk_size: Size of each counter in Spectral Bloom Filter
                       (Default - 4)
                       Default of 4 means that the maximum increment a counter can perform is 2**4, which is 16.
    :param remove_stopwords: To remove stopwords
                             (Default - True)
    :param tokens_path: Specifies the JSON file's path which contains user-given tokens.
                        By default, if tokens_path is not specified, Newspaper3k is used to scrape the html files. 
                        tokens_path has the following following format - 
                        {"filename1": [list of tokens for the HTML filename1], "filename2": [list of tokens for the HTML filename2]}

    It saves the search file in the output_file path.
    """

    files = get_all_html_files(directory)
    if tokens_path != None:
        all_tokens = get_all_tokens(tokens_path, files, directory)
    else:
        all_tokens = {f: [] for f in files}

    f = partial(process_file,
                false_positive=false_positive,
                chunk_size=chunk_size,
                remove_stopwords=remove_stopwords)

    search_index = [f(file, tokens=all_tokens[os.path.split(file)[-1]]) for file in files]

    with open(output_file, "w", encoding='utf8') as f:
        f.write(convert_2p15.HTML_TEMPLATE["HEAD"])
        f.write(convert_2p15.HTML_TEMPLATE["TAIL"].format(search_index))


def download_urls(json_file: str, output_file: str = "") -> None:
    """
    Downloads and saves HTML files using a JSON file containing list of URLs.
    (For Debugging purposes)
    """
    for url in json.load(open(json_file)):
        start = time.time()
        response = requests.get(url)
        print("Fetched {} in {} seconds.".format(url, time.time() - start))
        with open(output_file + response.url.replace("/", "") + "a.html",
                  "w",
                  encoding='utf8') as f:
            f.write(response.text)
        print("Saved at: " + output_file + response.url.replace("/", "") +
              "a.html")


if __name__ == "__main__":
    create_search_page("./htmls/",
                       output_file="search.html",
                       false_positive=0.01, tokens_path="./htmls/tokens.json")
    # download_urls("a.json")
