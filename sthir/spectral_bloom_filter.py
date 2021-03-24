from itertools import product
from math import ceil, log
from typing import Counter, Iterable, List

from bitarray import bitarray

from sthir.mmh3 import murmur3_x86_32 as mmh3_hash


class Hash_Funcs:
    """Class which creates the hash functions required for the Spectral Bloom filters."""
    def __init__(self, k: int, m: int):
        """
        Creates hash functions given m and k

        :param m: size of counter array
        :param k: number of hash functions
        """
        self.k = k
        self.hash_funcs_list = []
        for _ in range(self.k):
            self.hash_funcs_list.append(lambda x, s: mmh3_hash(x, seed=s) % m)

    def get_hashes(self, word: str) -> list:
        """
        Returns a list of k hashed indices for the input word

        :param word: Word to be hashed
        :returns: List of hashes of the word
        """
        return [self.hash_funcs_list[i](word, i) for i in range(self.k)]

    def check_hashes(self, word_list: list):
        """
        Logs the duplicate hashed indices for words in words_list

        :param word_list: List of words
        """
        faulty_words = set()
        for w in word_list:
            indices = self.get_hashes(w)
            res = Hash_Funcs.check_duplicates(indices)
            if res and res[1] not in faulty_words:
                faulty_words.add(res[1])

    @staticmethod
    def check_duplicates(indices_list: list):
        seen = set()
        for item in indices_list:
            if item in seen: return True, item
            seen.add(item)
        return False


class Spectral_Bloom_Filter:
    """
    Creates a Spectral Bloom Filter using the words parsed from the documents

    |  Paper: SIGMOD '03: Proceedings of the 2003 ACM SIGMOD international conference on Management of data, June 2003 Pages 241–252
    |  DOI: https://doi.org/10.1145/872757.872787
    """
    def create_hashes(self, token: str, hashes: int, max_length: int) -> list:
        """
        Get the hased indices for the string

        :param token: token to index
        :param hashes: no. of hashes (k)
        :param max_length: maximum length of the hash (m)
        :returns: list of hashes
        """
        return [
            mmh3_hash(key=token, seed=index) % max_length
            for index in range(hashes)
        ]

    def create_filter(self,
                      tokens: list,
                      p:float,
                      chunk_size: int = 4,
                      to_bitarray: bool = True,
                      bitarray_path: str = "document.bin") -> List[str]:
        """
        Creates a spectral bloom filter.

        |  Paper:  SIGMOD '03: Proceedings of the 2003 ACM SIGMOD international conference on Management of data, June 2003 Pages 241–252
        |  DOI: https://doi.org/10.1145/872757.872787

        :param tokens: List of words to index in spectral bloom filter
        :param p: The false postive rate
        :param chunk_size: Size of each counter in Spectral Bloom Filter (default: 4).
                           Default of 4 means that the maximum increment a counter.
                           Can perform is 2**4, which is 16.
        :param to_bitarray: If True, will convert and save as bitarray in bitarray_path.
                            If False, method will return list of lists containing 
                            the entire bitarray with chunks.
                            (Default: True).
        :param bitarray_path: Path to store the bitarray, (default:"document.bin").
        :returns: An array of binary strings
        """
        token_frq = Counter(tokens)
        upper_bound = 2**chunk_size - 1
        m,k = self.optimal_m_k(len(token_frq),p)
        sbf = [0] * m
        for word, frequency in token_frq.items():
            hash_indices = self.create_hashes(token=word,
                                              hashes=k,
                                              max_length=m)
            mn = min(map(sbf.__getitem__, hash_indices))
            for i in hash_indices:
                if sbf[i] == mn:
                    sbf[i] = min(sbf[i] + frequency, upper_bound)
        sbf = map(lambda x: bin(x)[2:].zfill(chunk_size), sbf)
        if to_bitarray == True:
            arr = bitarray("".join(sbf))
            arr.tofile(open(bitarray_path, 'wb'))
        return list(sbf)

    def optimal_m_k(self, n: int, p: int) -> tuple:
        """
        From: https://stackoverflow.com/questions/658439/how-many-hash-functions-does-my-bloom-filter-need

        :param n: items expected in filter
        :param p: false positive rate
        :param chunk_size: number of bits in each counter

        :returns: Tuple containing: 
                 m for number of bits needed in the bloom filter (index 0) and
                 k for number of hash functions we should apply (index 1)
        """
        m = (-n * log(p) / (log(2)**2))
        k = (m / n) * log(2)
        return (ceil(m), round(k))
