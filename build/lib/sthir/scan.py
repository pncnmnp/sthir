import sthir.spectral_bloom_filter as spectral_bloom_filter
import sthir.parse as parse

import sthir.convert_2p15 as convert_2p15
# import convert_2p15
import base64
import glob
import json
import requests
import time
from bitarray import bitarray
from sthir.generate_search import base2p15_encode
import lxml.html
import io

def get_all_html_files(directory):
    """
    Returns list of html files located in the directory
    """
    return glob.glob(directory+"/*.html")

def get_all_bin_files(directory):
    """
    Returns list of bin files located in the directory
    """
    return glob.glob(directory+"./*.bin")

def generate_bloom_filter(file, false_positive=0.1, chunk_size=4, remove_stopwords=True):
    """
    |  Generates a bloom filter and saves it in .bin file.
    |  The saved .bin filename is same as that of the .html file name.
    |  Returns a dictionary containing the - 
    |  length of the bitarray (m), no of hash functions used (k), chunk size (chunk_size), binary file name (bin_file), and HTML file's title (title).

    This method is internally used in method - create_search_page
    """
    spectral = spectral_bloom_filter.Spectral_Bloom_Filter()
    tokens = parse.extract_html_newspaper(file,remove_stopwords=remove_stopwords)

    title = lxml.html.parse(file).find(".//title").text

    no_items = len(tokens)
    m, k = spectral.optimal_m_k(no_items, false_positive)
    spectral.create_filter(tokens, m, 
                            chunk_size, k, 
                            to_bitarray=True, 
                            bitarray_path=file.replace(".html", ".bin"))
    return {
        "m": m,
        "k": k,
        "chunk_size": chunk_size,
        "bin_file": file.replace(".html", ".bin"),
        "title": title,
        "no_items": no_items
    }

def create_search_page(directory, output_file="search.html", false_positive=0.1, chunk_size=4, remove_stopwords=True):
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

    It saves the search file in the output_file path.
    """
    files = get_all_html_files(directory)
    bloom_meta = list()
    for file in files:
        bloom_meta.append(generate_bloom_filter(file, false_positive=false_positive, chunk_size=chunk_size, remove_stopwords=remove_stopwords))

    base2p15_arrs = list()
    for document in bloom_meta:
        bit_arr = bitarray()
        with open(document["bin_file"], "rb") as f:
            bit_arr.fromfile(f)

        base2p15_arrs.append([base2p15_encode(bit_arr.to01()), 
                                document["chunk_size"], 
                                document["m"], 
                                document["k"], document["bin_file"], document["title"], document["no_items"]])
        print("Scanned: {}".format(document["bin_file"]))

    with open(output_file, "w" ,encoding='utf8') as f:
        f.write(convert_2p15.HTML_TEMPLATE["HEAD"])
        f.write(convert_2p15.HTML_TEMPLATE["TAIL"].format(base2p15_arrs)  )

def download_urls(json_file, output_file=""):
    """
    Downloads and saves HTML files using a JSON file containing list of URLs.
    (For Debugging purposes)
    """
    for url in json.load(open(json_file)):
        start = time.time()
        response = requests.get(url)
        print("Fetched {} in {} seconds.".format(url, time.time() - start))
        with open(output_file+response.url.replace("/","")+"a.html", "w" ,encoding='utf8') as f:
            f.write(response.text)
        print("Saved at: " + output_file+response.url.replace("/","")+"a.html")

if __name__ == "__main__":
    create_search_page(".", output_file="search.html", false_positive=0.01)
    # download_urls("a.json")