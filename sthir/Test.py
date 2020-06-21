from collections import Counter

from logging import Formatter,FileHandler,getLogger
from logging import DEBUG 

from nltk.stem import WordNetLemmatizer 
from sthir.parse import extract_html_bs4
from sthir.spectral_bloom_filter import  Spectral_Bloom_Filter , Hash_Funcs
from typing import Iterable

import pkgutil
import io
import csv

from os.path import isfile , abspath , dirname ,join, isdir
from os import listdir

""""
Step1: Create a Tester object by passing your filename and parameters
Step2: Call the generate_Filter() method 
Step3: Call test_filter_for_FP() method
Step4: Check bloomfilter.log in current directory
"""


def create_logger():
    """Returns a well setup logger object for logging information."""
    logger = getLogger(name='SBF')
    logger.setLevel(DEBUG)

    formatter = Formatter(
        '%(asctime)s: %(name)s :- %(levelname)s: \n%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    file_handler = FileHandler(r'bloomfilter.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

class Tester:
    """Class for testing the spectal bloom filters"""
    def __init__(self, chunk_size:int = 4 , fp_rate:int = 0.1,remove_stopwords:bool=True , lemmetize:bool=False):
        """
        Constructs a Tester object for the Spectral Bloom Filters.
        :param chunk_size: Size in bits of each counter in the Spectal Bloom Filter.
                           *(Default - 4)*
        :param fp_rate: False_postive rate for the Spectral Bloom Filter.
                           *(Default - 0.1)* 
        :param remove_stopwords: Boolean value for enabling/disabling stopword removal.
        :param lemmetize: Boolean value for enabling/disabling lemmetization of words.                         
        :returns: Object of Tester class
        """
        #Set all four varaibles
        self.chunk_size = chunk_size
        self.fp_rate = fp_rate
        self.lemmetize = lemmetize
        self.remove_stopwords = remove_stopwords
        self.max_word_count = 2 ** self.chunk_size - 1 # max_count the counters can read

        self.logger  = create_logger()
        self.read_dict_words()
        self.no_of_words = len(self.testing_words)

    def read_dict_words(self):
        """
        Reads english_dict.txt file in resources and creates a list of words.
        """
        dataString = pkgutil.get_data( "sthir", "resources/english_dict.txt")
        l = [ str(i)[2:-1] for i in dataString.splitlines()]
        l = [ word.strip() for word in l]
        if self.lemmetize: 
            lemmatizer = WordNetLemmatizer() 
            l = [ lemmatizer.lemmatize(word) for word in l ]
        self.testing_words = l
        
    def generate_Filter(self, doc_path:str )->None:
        """
        Generates a Spectral Bloom filter for the specified document.
        :param doc_name: Name or Path to the File
        :returns: None
        """
        self.doc_path = doc_path

        self.spectral = Spectral_Bloom_Filter()
        self.tokens = extract_html_bs4(self.doc_path ,self.remove_stopwords , self.lemmetize )

        self.n = len(self.tokens)
        self.m, self.k = self.spectral.optimal_m_k(self.n, self.fp_rate)
        
        self.logger.info( 
            "\tNo_of_words:{} Count_array_size:{} No_of_hashes:{} \n\terror_rate:{} ".format(self.n, self.m, self.k, self.fp_rate)
        )

        self.counter =  self.spectral.create_filter( self.tokens, self.m, self.chunk_size, self.k,
            method="minimum", to_bitarray=False
        )
 

    def test_filter(self, doc_path:str):
        """Tests and logs the stats after testing the single provided file.
        :returns: None
        """
        if not isfile(doc_path):
            raise Exception(f"{doc_path} file does not exist.")

        self.generate_Filter(doc_path)

        word_counts = Counter(self.tokens)

        hash_funcs = Hash_Funcs(k=self.k, m= self.m)

        fp_count , no_of_unseen_words = 0 , 0
        wrong_count , seen_words = 0 , 0

        #Loop that iterates through the testing_words
        for word in self.testing_words:

            #Querying the filter
            hashed_indices = hash_funcs.get_hashes(word)
            values = [ int(self.counter[i],2) for i in hashed_indices]
            SBF_ans = min(values)               #Filter's prediction
            current_count = word_counts[word] #Actual count in the document

            if current_count == 0:                  # word is absent in the filter
                no_of_unseen_words += 1
                if SBF_ans != 0: fp_count += 1      #It is a false postive
            else:                                   #word was inserted
                seen_words += 1
                if SBF_ans != current_count:
                    if SBF_ans == self.max_word_count and current_count >= self.max_word_count:
                        # The no of occurences of the word is greater than or equal to 
                        # the max_word_count and the  SBF prediction is exactly equal 
                        # to the max_word_count. So SBF was correct!
                        continue
                    else:
                        wrong_count += 1

        # Headers for the csv file                
        headers = [
            'Filename', 'Error_rate' , 'No_of_hashes(k)' , 'Chunk_size', 'Filter-size(m)' , 
            'Inserted Words in dict' , 'Count_Mismatches' , 'Error in counts',
             'New words', 'False Positives', 'FP_Error'
        ]

        #Entry for the csv file
        entry = [
                self.doc_path, self.fp_rate , self.k , self.chunk_size, self.m ,
                seen_words, wrong_count , wrong_count / seen_words,
                no_of_unseen_words , fp_count ,fp_count / no_of_unseen_words
             ]
        
        file_path = abspath(self.doc_path)

        csv_file = join(  dirname(file_path) , 'stats.csv')
        # print(csv_file)

        if isfile( csv_file ): 
            with open(csv_file, 'a') as f:   
                writer = csv.writer(f)
                writer.writerow(entry)
        else:
            with open(csv_file, 'w',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(entry)


        self.logger.warning( 
            "\tNo of words in word-dictionary: {}\n".format( self.no_of_words ) +
            "\tNo of unseen words in dictionary: {}\n".format( no_of_unseen_words ) +
            "\tFalse postives found: {}\n".format(fp_count)  +
            "\tFP_count / No_of_unseen_words: {}\n".format(fp_count / no_of_unseen_words) +   
            "\tNo of inserted words found in dictionary: {}\n".format(seen_words) +
            "\tWrong word counts: {}\n".format( wrong_count) + 
            "\tTheoretical error_probability: {}\n".format( 0.5 ** self.k ) +
            "\tTotal Error: {}\n".format( (fp_count+wrong_count) / self.no_of_words )  
        )


    def test_dir(self, dir_path:str)-> None :
        """Tests and creates stats.csv and common_stats.txt 
        file providing stats after testing all the html files in directory against words in the directory.
        :returns: None
        """
        if not isdir(dir_path):
            raise Exception(f"{dir_path} is not a valid directory.")

        abs_dir_path = abspath( dir_path )
        csv_file = join(  abs_dir_path , 'stats.csv')
        txt_file=  join(  abs_dir_path , 'common_stats.csv')

        commomn_stats = f'Chunk size:{self.chunk_size}\n' + f'Error rate:{self.fp_rate}'

        with open(txt_file,'w',encoding='utf8') as txtfile:
            txtfile.write(commomn_stats)
        

        for current_file in listdir(abs_dir_path):

            if current_file.endswith(".html"):
                current_file_path = join(  abs_dir_path , current_file )

                self.generate_Filter( current_file_path)
                hash_funcs = Hash_Funcs(k=self.k, m= self.m)

                word_counts = Counter(self.tokens)
                fp_count , no_of_unseen_words = 0 , 0

                wrong_count , seen_words = 0 , 0

                #Loop that iterates through the testing_words
                for word in self.testing_words:

                    #Querying the filter
                    hashed_indices = hash_funcs.get_hashes(word)
                    values = [ int(self.counter[i],2) for i in hashed_indices]
                    SBF_ans = min(values)               #Filter's prediction
                    current_count = word_counts[word] #Actual count in the document

                    if current_count == 0:                  # word is absent in the filter
                        no_of_unseen_words += 1
                        if SBF_ans != 0: fp_count += 1      #It is a false postive
                    else:                                   #word was inserted
                        seen_words += 1
                        if SBF_ans != current_count:
                            if SBF_ans == self.max_word_count and current_count >= self.max_word_count:
                                # The no of occurences of the word is greater than or equal to 
                                # the max_word_count and the  SBF prediction is exactly equal 
                                # to the max_word_count. So SBF was correct!
                                continue
                            else:
                                wrong_count += 1

                # Headers for the csv file                
                headers = [
                    'Filename', 'No_of_hashes(k)' , 'Filter-size(m)' , 
                    'Inserted Words in dict' , 'Count_Mismatches' , 'Error in counts',
                    'New words', 'False Positives', 'FP_Error'
                ]

                #Entry for the csv file
                entry = [
                        current_file, self.k , self.m ,
                        seen_words, wrong_count , round( wrong_count / seen_words,10),
                        no_of_unseen_words , fp_count ,round(fp_count / no_of_unseen_words , 10)
                    ]
                
                if isfile( csv_file ): 
                    with open(csv_file, 'a') as f:   
                        writer = csv.writer(f)
                        writer.writerow(entry)
                else:
                    with open(csv_file, 'w',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerow(entry)
