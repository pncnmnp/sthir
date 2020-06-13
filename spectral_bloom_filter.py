from typing import *
from sys import getsizeof

import bitarray
from mmh3 import hash as mmh3_hash
import itertools
import math
import logging

class Hash_Funcs:
    def __init__( self, k:int, m:int):
        """
        Creates optimal number of hash functions given m and n
            m - size of counter array
        """
        self.k = k
        self.hash_funcs_list = []
        for i in range(self.k):
            self.hash_funcs_list.append( lambda x,s : mmh3_hash( x , seed = s, signed=False) % m )

    def get_hashes(self, word:str )->list:
        """Returns a list of k hashed indices for the input word"""
        return [ self.hash_funcs_list[i](word , i) for i in range(self.k)]

    def check_hashes(self , word_list:list):
        """Logs the duplicate hashed indices for words in words_list"""
        faulty_words = set()
        for w in word_list:
            indices = self.get_hashes(w)
            res = hash_funcs.check_duplicates(indices)
            if res and res[1] not in faulty_words:
                faulty_words.add(res[1])
                logger.warning(
                    '\tWord:{} \n\tIndices:{} \n\tRepeated:{}'.format(
                        w, indices, res[1]))

    @staticmethod
    def check_duplicates(indices_list: list):
        seen = set()
        for item in indices_list:
            if item in seen: return True, item
            seen.add(item)
        return False


class Spectral_Bloom_Filter:
    # k - no of hash functions
    # m - size of bit array
    # n - no of words in the document

    def __init__(self, error_rate: float = 0.01):
        self.error_rate = error_rate

    def initialize_string(self, length: int):
        return ('0' * length)

    def gen_counter_chunks(self,
                           string: str,
                           chunk_size: int,
                           drop_remaining: bool = False) -> Iterator[str]:
        """
        Yields an iterator of chunks of specified size

        If drop_remaining is specified, the iterator is guaranteed to have  
        all chunks of same size.

        >>> list(gen_counter_chunks('123456789A', 4)) == ['1234', '5678', '9A']
        >>> list(gen_counter_chunks('123456789A', 4, drop_remaining = True)) == ['1234', '5678']

        :param string: The string to chunk
        :type string: str
        :param chunk_size: Size of individual chunk, the string will split in 
        :type chunk_size: int
        :param drop_remaining: Remove final chunks of invalid length, defaults to False
        :type drop_remaining: bool, optional
        :yield: A chunk of string of specified size
        :rtype: Iterator[str]
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

        Params: counter_length - No. of bits in each counter
        
        Returns: Dictionary used for binary counter operation
        """
        digits = list(map(''.join, list(itertools.product('01', repeat=counter_length))))

        bin_counter = {curr: incr for curr,incr in zip(digits, (digits[1:] + [digits[0]]))}

        # We don't want last index to be something like '1111' -> '0000',
        # Instead we want something like '1111' -> '1111' (i.e. remain at last position)
        last_index = list(bin_counter.keys())[-1]
        bin_counter[last_index] = last_index

        return bin_counter

    def create_hashes(self, token:str, hashes:int, max_length:int) -> list:
        """
        Get the hased indices for the string
        """
        return [mmh3_hash(key=token, seed=index, signed=False)%max_length for index in range(hashes)]

    def create_filter(self, tokens:list, length:int, chunk_size:int=4, no_hashes:int=5, method:str="minimum") -> bitarray:
        bin_arr = self.initialize_string(length)

        counter = list(self.gen_counter_chunks(bin_arr, chunk_size, drop_remaining=True))
        bin_incr = self.init_counter(chunk_size)

        counter_size = len(counter)
        hash_funcs = Hash_Funcs(k=no_hashes, m=counter_size)

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

        return counter

    def optimal_m_k(self, n:int, p:int, chunk_size:int) -> tuple:
        """
        From: https://stackoverflow.com/questions/658439/how-many-hash-functions-does-my-bloom-filter-need

        Params: n - items expected in filter
                p - false positive rate
                chunk_size - number of bits in each counter

        Returns: m - number of bits needed in the bloom filter
                 k - number of hash functions we should apply
        """
        m = (-n*math.log(p) / (math.log(2)**2))
        k = (m/n)*math.log(2)
        return (int(m)*chunk_size, int(k))

if __name__ == "__main__":
    #logging
    logger = logging.getLogger(name='SBF')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s: %(name)s :- %(levelname)s: \n%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    file_handler = logging.FileHandler('bloomfilter.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


    spectral = Spectral_Bloom_Filter()

    chunk_size = 4
    no_items = 6
    false_positive = 0.001

    # logger.info( "\tNo_of_words:{} Count_array_size:{} No_of_hashes:{} ,\n\terror_rate:{}".format(n, m , hashes.k,error_rate) )

    m, k = spectral.optimal_m_k(no_items, false_positive, chunk_size)
    print(m, k)
    print(spectral.create_filter("hello world this is parth parikh! hello".split(" "), m, chunk_size, k))