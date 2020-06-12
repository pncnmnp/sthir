import bitarray
import mmh3 # For murmurhash3
import itertools
from typing import *
from math import log2


class Spectral_Bloom_Filter:
    def __init__(self,error_rate:float=0.01):
        self.error_rate = error_rate

    def initialize_string(self, length:int):
        return ('0'*length)
    
    def init_counter(self, counter_length:int) -> dict:
        """
        To initialize a binary counter for incrementing 
        Spectral Bloom Filter's counters.

        Example: For counter_length = 2
        Method returns - {'00': '01', '01': '10', '10': '11', '11': '11'}

        Params: counter_length - No. of bits in each counter
        
        Returns: Dictionary used for binary counter operation
        # Look in chat ok!
        """
        size = log2(counter_length)
        digits = list(map(''.join, list(itertools.product('01', repeat=size))))

        bin_counter = {curr: incr for curr,incr in zip(digits, (digits[1:] + [digits[0]]))}

        # We don't want last index to be something like '1111' -> '0000',
        # Instead we want something like '1111' -> '1111' (i.e. remain at last position)
        last_index = list(bin_counter.keys())[-1]
        bin_counter[last_index] = last_index

        return bin_counter
