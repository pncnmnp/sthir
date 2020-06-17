import spectral_bloom_filter
import parse
import convert_2p15
import base64
import glob
import json
import requests
import time
from bitarray import bitarray
from generate_search import base2p15_encode
import lxml.html

def get_all_html_files(directory):
    return glob.glob(directory+"/*.html")

def get_all_bin_files(directory):
    return glob.glob("./*.bin")

def generate_bloom_filter(file, false_positive=0.1, chunk_size=4, remove_stopwords=True):
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
        "title": title
    }

def create_search_page(directory, output_file="search.html", false_positive=0.1, chunk_size=4, remove_stopwords=True):
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
                                document["k"], document["bin_file"], document["title"]])
        print("Scanned: {}".format(document["bin_file"]))

    with open(output_file, "w") as f:
        f.write(convert_2p15.HTML_TEMPLATE["HEAD"])
        f.write(convert_2p15.HTML_TEMPLATE["TAIL"].format(base2p15_arrs))

def download_urls(json_file, output_file=""):
    for url in json.load(open(json_file)):
        start = time.time()
        response = requests.get(url)
        print("Fetched {} in {} seconds.".format(url, time.time() - start))
        with open(output_file+response.url.replace("/","")+"a.html", "w") as f:
            f.write(response.text)
        print("Saved at: " + output_file+response.url.replace("/","")+"a.html")

if __name__ == "__main__":
    # create_search_page(".", output_file="out.html", false_positive=0.01)
    download_urls("a.json")