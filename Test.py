import parse
from spectral_bloom_filter import *
from collections import Counter
from typing import Iterable

""""
Step1: Add your html file to Testing.py
Step2: Create a Tester object by passing your filename and parameters
Step3: Call test_filter() method
Step4: Check the Log
"""


def create_logger():
    """Returns a logger object"""
    logger = logging.getLogger(name='SBF')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s: %(name)s :- %(levelname)s: \n%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    file_handler = logging.FileHandler('bloomfilter.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

class Tester:
    def __init__(self, doc_name:str , chunk_size:int = 4 , fp_rate:int = 0.1):
        """doc_name is the name of the file in the Testing directory"""
        self.doc_name = doc_name
        self.chunk_size = chunk_size
        self.fp_rate = fp_rate
        self.logger  = create_logger()


    def generate_Filter(self):
        """
        Returns the counter and params for the specified document in Testing Folder
        """
        self.FILE = "Testing\\" + self.doc_name

        self.spectral = Spectral_Bloom_Filter()
        self.tokens = parse.extract_html_bs4(self.FILE)

        self.n = len(self.tokens)
        self.m, self.k = self.spectral.optimal_m_k(self.n, self.fp_rate)

        # self.bin_counter = spectral.init_counter(chunk_size)
        
        self.logger.info( 
            "\tNo_of_words:{} Count_array_size:{} No_of_hashes:{} ,\n\terror_rate:{}".format(self.n, self.m, self.k,self.fp_rate)
        )

        self.counter =  self.spectral.create_filter( self.tokens, self.m, self.chunk_size, self.k,
            method="minimum", to_bitarray=False
        )

    @staticmethod
    def read_dict_words():
        """Reads and returns a list of words in the english_dict.txt file"""
        f = open(r"Testing\english_dict.txt",'r')
        l = f.readlines()
        l = [ word.strip() for word in l]
        return l

    def test_filter(self):
        """Tests and logs the stats after testing the provided file"""
        self.generate_Filter()  
        word_counts = Counter(self.tokens)

        # print(word_counts)

        testing_words = Tester.read_dict_words()
        no_of_words = len(testing_words)

        hash_funcs = Hash_Funcs(k=self.k, m= self.m)

        fp_count , no_of_unseen_words = 0 , 0
        #Loop that iterates through the 
        for word in testing_words:
            if word_counts[word] == 0:
                # word is absent in the filter
                no_of_unseen_words += 1
                hashed_indices = hash_funcs.get_hashes(word)
                values = [ int(self.counter[i],2) for i in hashed_indices]
                SBF_ans = min(values) #Filter's prediction
                if SBF_ans != 0: #It is a false postive
                    fp_count += 1
            
        self.logger.warning( 
            "\tTotal no unseen words: {}\n".format( no_of_unseen_words ) +
            "\tNo of false_postives found: {}\n".format(fp_count)  +
            "\tFP_count / No_of_unseen_words: {}".format(fp_count / no_of_unseen_words)    
        )



if __name__ == "__main__":
    
    #Keep the html file in ./Testing/
    file_name = r"Algorithms interviews_ theory vs. practice.html"

    test_obj = Tester(file_name , chunk_size= 4 , fp_rate= 0.01)
    test_obj.test_filter()

    # print( test_obj.counter[:10] )
