from collections import Counter
from math import ceil, log
from typing import List

from sthir.mmh3 import murmur3_x86_32 as mmh3_hash


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

    def create_filter(
        self,
        tokens: list,
        p: float,
        chunk_size: int = 4,
    ) -> List[str]:
        """
        Creates a spectral bloom filter.

        |  Paper:  SIGMOD '03: Proceedings of the 2003 ACM SIGMOD international conference on Management of data, June 2003 Pages 241–252
        |  DOI: https://doi.org/10.1145/872757.872787

        :param tokens: List of words to index in spectral bloom filter
        :param p: The false postive rate
        :param chunk_size: Size of each counter in Spectral Bloom Filter (default: 4).
                           Default of 4 means that the maximum increment a counter.
                           Can perform is 2**4, which is 16.
        :returns: A list of binary strings
        """
        token_frq = Counter(tokens)
        upper_bound = 2**chunk_size - 1
        m, k = self.optimal_m_k(len(token_frq), p)
        sbf = [0] * m
        for word, frequency in token_frq.items():
            hash_indices = self.create_hashes(token=word,
                                              hashes=k,
                                              max_length=m)
            mn = min(map(sbf.__getitem__, hash_indices))
            for i in hash_indices:
                if sbf[i] == mn:
                    sbf[i] = min(sbf[i] + frequency, upper_bound)
        sbf = list(map(lambda x: bin(x)[2:].zfill(chunk_size), sbf))
        return sbf

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
