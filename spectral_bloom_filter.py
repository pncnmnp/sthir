import bitarray
import mmh3  # For murmurhash3
import itertools
from typing import *
from math import log2


class Spectral_Bloom_Filter:
    def __init__(self, error_rate: float = 0.01):
        self.error_rate = error_rate

    def initialize_string(self, length: int):
        return ('0' * length)

    def gen_counter_chunks(self,
                           string: str,
                           chunk_size: int,
                           drop_remaining: bool = False) -> Iterable[str]:
        """
            Yields an iterator of chunks of specified size

            If drop_remaining is specified, the iterator is guaranteed to have  
            all chunks of same size.

            >>> list(gen_counter_chunks('123456789A', 4)) == ['1234', '5678', '9A']
            >>> list(gen_counter_chunks('123456789A', 4, drop_remaining = True)) == ['1234', '5678']
            """
        string_length = len(string)

        # If drop remaining is True, trim the string
        if drop_remaining and string_length % chunk_size != 0:
            closest_multiple = string_length - string_length % chunk_size
            string = string[:closest_multiple]

        for c in range(0, len(string), chunk_size):
            yield string[c:c + chunk_size]

    def init_counter(self, counter_length: int) -> dict:
        """
        To initialize a binary counter for incrementing 
        Spectral Bloom Filter's counters.

        Example: For counter_length = 2
        Method returns - {'00': '01', '01': '10', '10': '11', '11': '11'}

        Params: counter_length - No. of bits in each counter
        
        Returns: Dictionary used for binary counter operation
        """
        size = log2(counter_length)
        digits = list(map(''.join, list(itertools.product('01', repeat=size))))

        bin_counter = {
            curr: incr
            for curr, incr in zip(digits, (digits[1:] + [digits[0]]))
        }

        # We don't want last index to be something like '1111' -> '0000',
        # Instead we want something like '1111' -> '1111' (i.e. remain at last position)
        last_index = list(bin_counter.keys())[-1]
        bin_counter[last_index] = last_index

        return bin_counter
