from bitarray import bitarray
from itertools import product

from sthir.mmh3 import murmur3_x86_32 as mmh3_hash
from math import log , ceil

from sys import getsizeof
from typing import List , Iterable


class Hash_Funcs:
    """Class which creates the hash functions required for the Spectral Bloom filters."""
    def __init__( self, k:int, m:int):
        """
        Creates hash functions given m and k

        :param m: size of counter array
        :param k: number of hash functions
        """
        self.k = k
        self.hash_funcs_list = []
        for _ in range(self.k):
            self.hash_funcs_list.append( lambda x,s : mmh3_hash( x , seed = s) % m )

    def get_hashes(self, word:str )->list:
        """
        Returns a list of k hashed indices for the input word

        :param word: Word to be hashed
        :returns: List of hashes of the word
        """
        return [ self.hash_funcs_list[i](word , i) for i in range(self.k)]

    def check_hashes(self , word_list:list):
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
    def check_duplicates(indices_list:list):
        seen = set()
        for item in indices_list:
            if item in seen:  return True , item
            seen.add(item)
        return False

class Spectral_Bloom_Filter:
    """
    Creates a Spectral Bloom Filter using the words parsed from the documents

    |  Paper: SIGMOD '03: Proceedings of the 2003 ACM SIGMOD international conference on Management of data, June 2003 Pages 241–252
    |  DOI: https://doi.org/10.1145/872757.872787
    """

    def initialize_string(self, length:int):
        """
        Returns string of zeros of width "length".

        :param length: size of the string
        :returns: string of 0s of the specified length
        """
        return ('0'*length)

    def gen_counter_chunks(self, string: str, chunk_size:int, drop_remaining:bool=False) -> Iterable[str]: 
        """
        Yields an iterator of chunks of specified size

        If drop_remaining is specified, the iterator is guaranteed to have  
        all chunks of same size.

        >>> list(gen_counter_chunks('123456789A', 4)) == ['1234', '5678', '9A']
        >>> list(gen_counter_chunks('123456789A', 4, drop_remaining = True)) == ['1234', '5678']

        :param string: bit string whose chunks are to be obtained
        :param chunk_size: size of each chunk (optimal: 4)
        :param drop_remaining: to drop the extra string, if left, (default: False)
        :returns: generator object containing the list of chunks
        """
        string_length = len(string)

        # If drop remaining is True, trim the string
        if drop_remaining and string_length % chunk_size != 0:
            closest_multiple = string_length - string_length % chunk_size
            string = string[:closest_multiple]

        for c in range(0, len(string), chunk_size):
            yield string[c:c + chunk_size]
    
    def init_counter(self, counter_length:int) -> dict:
        """
        To initialize a binary counter for incrementing 
        Spectral Bloom Filter's counters.

        Example: For counter_length = 2
        Method returns - {'00': '01', '01': '10', '10': '11', '11': '11'}

        :param counter_length: No. of bits in each counter
        :returns: Dictionary used for binary counter operation
        """
        digits = list(map(''.join, list( product('01', repeat=counter_length) )))

        bin_counter = {curr: incr for curr,incr in zip(digits, (digits[1:] + [digits[0]]))}

        # We don't want last index to be something like '1111' -> '0000',
        # Instead we want something like '1111' -> '1111' (i.e. remain at last position)
        last_index = list(bin_counter.keys())[-1]
        bin_counter[last_index] = last_index

        return bin_counter

    def create_hashes(self, token:str, hashes:int, max_length:int) -> list:
        """
        Get the hased indices for the string

        :param token: token to index
        :param hashes: no. of hashes (k)
        :param max_length: maximum length of the hash (m)
        :returns: list of hashes
        """
        return [mmh3_hash(key=token, seed=index)%max_length for index in range(hashes)]

    def create_filter(self, tokens:list, m:int, 
                            chunk_size:int=4, no_hashes:int=5, 
                            method:str="minimum", to_bitarray:bool=True, 
                            bitarray_path:str="document.bin") -> bitarray:
        """
        Creates a spectral bloom filter.

        |  Paper:  SIGMOD '03: Proceedings of the 2003 ACM SIGMOD international conference on Management of data, June 2003 Pages 241–252
        |  DOI: https://doi.org/10.1145/872757.872787

        :param tokens: List of words to index in spectral bloom filter
        :param m: size of the bitarray
        :param chunk_size: Size of each counter in Spectral Bloom Filter (default: 4).
                           Default of 4 means that the maximum increment a counter.
                           Can perform is 2**4, which is 16.
        :param no_hashes: No. of hashes to index word with, (default: 5)
        :param method: Currently only "minimum" is supported, (default: "minimum").
                       "minimum" stands for Minimum Increment
        :param to_bitarray: If True, will convert and save as bitarray in bitarray_path.
                            If False, method will return list of lists containing 
                            the entire bitarray with chunks.
                            (Default: True).
        :param bitarray_path: Path to store the bitarray, (default:"document.bin").
        """
        bin_arr = self.initialize_string(m*chunk_size)

        counter = list(self.gen_counter_chunks(bin_arr, chunk_size, drop_remaining=True))
        bin_incr = self.init_counter(chunk_size)

        hash_funcs = Hash_Funcs(k=no_hashes, m=m)

        for token in tokens:
            hashed_indices = hash_funcs.get_hashes(token)

            values_indices = [counter[i] for i in hashed_indices]
            min_val = min(values_indices)

            if method == "minimum":
                # increment counter at hashed_indices
                # USING MINIMUM INCREMENT
                for index in hashed_indices:
                    if counter[index] == min_val:
                        counter[index] = bin_incr[counter[index]]
                # print(token, hashed_indices, counter, min_val, values_indices)

        print("Size of the filter is: {} bytes".format(getsizeof(''.join(counter))))
        # print("".join(counter))

        if to_bitarray == True:
            arr = bitarray("".join(counter))
            arr.tofile(open(bitarray_path, 'wb'))
        else:
            return counter

    def optimal_m_k(self, n:int, p:int) -> tuple:
        """
        From: https://stackoverflow.com/questions/658439/how-many-hash-functions-does-my-bloom-filter-need

        :param n: items expected in filter
        :param p: false positive rate
        :param chunk_size: number of bits in each counter

        :returns: Tuple containing: 
                 m for number of bits needed in the bloom filter (index 0) and
                 k for number of hash functions we should apply (index 1)
        """
        m = (-n*log(p) / (log(2)**2))
        k = (m/n)*log(2)
        return ( ceil(m), round(k))