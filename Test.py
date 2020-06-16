from collections import Counter

#To be removed
from logging import Formatter,FileHandler,getLogger
from logging import DEBUG 

from nltk.stem import WordNetLemmatizer 
from parse import extract_html_bs4
from spectral_bloom_filter import  Spectral_Bloom_Filter , Hash_Funcs
from typing import Iterable



""""
Step1: Add your html file to Testing.py
Step2: Create a Tester object by passing your filename and parameters
Step3: Call the generate_Filter() method 
Step4: Call test_filter() method
Step5: Check ./Testing/bloomfilter.log
"""


def create_logger():
    """Returns a logger object"""
    logger = getLogger(name='SBF')
    logger.setLevel(DEBUG)

    formatter = Formatter(
        '%(asctime)s: %(name)s :- %(levelname)s: \n%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    file_handler = FileHandler(r'Testing\bloomfilter.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

class Tester:
    """Class for testing the bloom filters"""
    def __init__(self, doc_name:str , chunk_size:int = 4 , fp_rate:int = 0.1):
        """doc_name is the name of the file in the Testing directory"""
        self.doc_name = doc_name
        self.chunk_size = chunk_size
        self.fp_rate = fp_rate
        self.logger  = create_logger()


    def generate_Filter(self , remove_stopwords , lemmetize):
        """
        Returns the counter and params for the specified document in Testing Folder
        """
        self.lemmetize = lemmetize

        self.FILE = "Testing\\" + self.doc_name

        self.spectral = Spectral_Bloom_Filter()
        self.tokens = extract_html_bs4(self.FILE ,remove_stopwords , lemmetize )

        self.n = len(self.tokens)
        self.m, self.k = self.spectral.optimal_m_k(self.n, self.fp_rate)
        
        self.logger.info( 
            "\tNo_of_words:{} Count_array_size:{} No_of_hashes:{} \n\terror_rate:{} ".format(self.n, self.m, self.k, self.fp_rate)
        )

        self.counter =  self.spectral.create_filter( self.tokens, self.m, self.chunk_size, self.k,
            method="minimum", to_bitarray=False
        )


    def read_dict_words(self):
        """Reads and returns a list of words in the english_dict.txt file"""
        f = open(r"Testing\english_dict.txt",'r')
        l = f.readlines()
        l = [ word.strip() for word in l]
        if self.lemmetize: 
            lemmatizer = WordNetLemmatizer() 
            l = [ lemmatizer.lemmatize(word) for word in l ]
        return l

    def test_filter_for_FP(self):
        """Tests and logs the stats after testing the provided file"""
        word_counts = Counter(self.tokens)

        testing_words = self.read_dict_words()

        no_of_words = len(testing_words)

        hash_funcs = Hash_Funcs(k=self.k, m= self.m)

        fp_count , no_of_unseen_words = 0 , 0

        wrong_count , seen_words = 0 , 0

        #Loop that iterates through the testing_words
        for word in testing_words:

            #Querying the filter
            hashed_indices = hash_funcs.get_hashes(word)
            values = [ int(self.counter[i],2) for i in hashed_indices]
            SBF_ans = min(values) #Filter's prediction
            current_count = word_counts[word]

            if current_count == 0:                  # word is absent in the filter
                no_of_unseen_words += 1
                if SBF_ans != 0: fp_count += 1      #It is a false postive
            else:                                   #word was inserted
                seen_words += 1
                if SBF_ans != current_count:
                    wrong_count += 1 

            
        self.logger.warning( 
            "\tNo of words in word-dictionary: {}\n".format( no_of_words ) +
            "\tNo of unseen words in dictionary: {}\n".format( no_of_unseen_words ) +
            "\tFalse postives found: {}\n".format(fp_count)  +
            "\tFP_count / No_of_unseen_words: {}\n".format(fp_count / no_of_unseen_words) +   
            "\tNo of inserted words found in dictionary: {}\n".format(seen_words) +
            "\tWrong word counts: {}\n".format( wrong_count) + 
            "\tTheoretical error_probability: {}\n".format( 0.5 ** self.k ) +
            "\tTotal Error: {}\n".format( (fp_count+wrong_count) / no_of_words )  
        )


if __name__ == "__main__":
    
    #Keep the html file in ./Testing/
    file_name = r"Algorithms interviews_ theory vs. practice.html"

    test_obj = Tester(file_name , chunk_size= 4 , fp_rate= 0.1)
    test_obj.generate_Filter( True, False )
    test_obj.test_filter_for_FP()

