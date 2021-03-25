from collections import Counter

from logging import Formatter,FileHandler,getLogger
from logging import DEBUG 

# from mmh3 import murmur3_x86_32 as mmh3_hash
from mmh3 import one_at_a_time as mmh3_hash

from nltk.stem import WordNetLemmatizer 
from parse import extract_html_newspaper
from spectral_bloom_filter import  Spectral_Bloom_Filter 

from typing import Iterable

import pkgutil
# import io
import csv

from os.path import isfile , abspath , dirname ,join, isdir
from os import listdir

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


def _create_logger():
    """
    Returns a well setup logger object for logging the statistics after testing the 
    Bloom Filters.
    """
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
    """
    Class for testing the accuracy of Spectal Bloom Filters on a large
    list of frequently used English words.

    Parameters
    ----------
    chunk_size: int, optional
        Size in bits of each counter in the Spectal Bloom Filter.
        Default ``14``.
    fp_rate: float, optional
        False_postive rate for the Spectral Bloom Filter.
        Default ``0.1``.
    remove_stopwords: bool, optional
        Boolean flag for enabling/disabling stopword removal.
        Default ``True`.
    lemmetize: bool, optional
        Boolean flag for enabling/disabling lemmetization of words.
        Default ``True`.

    Example
    --------
        >>> from sthir.test import Tester
        >>> obj = Tester()
        >>> # Test on single files
        >>> obj.test_filter_for_file('sample.html') 
        Size of the filter is: 1000 bytes
        >>> # Test on an entire directory
        >>> obj.test_dir('folder_with_html_files') 
        Size of the filter is: 1000 bytes
        Size of the filter is: 2000 bytes
        ...   
    """

    def __init__(self, chunk_size:int = 4 , fp_rate:int = 0.1,remove_stopwords:bool=True , lemmetize:bool=False):

        #Set all four necessary input for SBF
        self.chunk_size = chunk_size
        self.fp_rate = fp_rate
        self.lemmetize = lemmetize
        self.remove_stopwords = remove_stopwords

        # max_count the counters can count upto
        self.max_word_count = 2 ** self.chunk_size - 1 

        # logger object
        self.logger  = _create_logger()

        # Load the testing_words
        self.testing_words = self.__read_dict_words()
        self.no_of_words = len(self.testing_words)

    def __read_dict_words(self):
        """
        Reads english_dict.txt file from the resources and creates a list of words
        on which the SBF(s) will be tested.
        """
        dataString = pkgutil.get_data( "sthir", "resources/english_dict.txt")
        l = [ str(i)[2:-1] for i in dataString.splitlines()]
        l = [ word.strip() for word in l]
        if self.lemmetize: 
            lemmatizer = WordNetLemmatizer() 
            l = [ lemmatizer.lemmatize(word) for word in l ]
        return l
        
    def __generate_Filter(self, doc_path:str )->None:
        """
        Generates a Spectral Bloom filter for the specified document.
        Parameters
        ----------
        doc_name: str
            Path of the html file whose .
        """
        self.doc_path = doc_path

        self.spectral = Spectral_Bloom_Filter()
        self.tokens = extract_html_newspaper(self.doc_path ,self.remove_stopwords , self.lemmetize )

        self.n = len(set(self.tokens))

        self.m, self.k = self.spectral.optimal_m_k(self.n, self.fp_rate)
        
        self.logger.info( 
            "\tNo_of_words:{} Count_array_size:{} No_of_hashes:{} \n\terror_rate:{} ".format(self.n, self.m, self.k, self.fp_rate)
        )

        self.counter =  self.spectral.create_filter( 
            self.tokens, self.fp_rate, self.chunk_size
        )

    def test_filter_for_file(self, doc_path:str):
        """
        Tests and logs the stats after testing the single provided file in stats.csv and
        bloomfilter.log.
        """
        if not isfile(doc_path):
            raise Exception(f"{doc_path} file does not exist.")

        self.__generate_Filter(doc_path)

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
                        # the max_word_count and the SBF prediction is exactly equal 
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

        # Single Entry for the csv file
        entry = [
                self.doc_path, self.fp_rate , self.k , self.chunk_size, self.m ,
                seen_words, wrong_count , wrong_count / seen_words,
                no_of_unseen_words , fp_count ,fp_count / no_of_unseen_words
             ]
        
        file_path = abspath(self.doc_path)

        csv_file = join(  dirname(file_path) , 'stats.csv')

        if isfile( csv_file ): 
            with open(csv_file, 'a') as f:   
                writer = csv.writer(f)
                writer.writerow(entry)
        else:
            with open(csv_file, 'w',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(entry)

        # Logging the stats in the log file.
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
        """
        Tests and creates *stats.csv* and *common_stats.txt* file providing 
        relevant stats after testing all the html files 
        in directory "dir_path" against the test words in a large dictionary.
        """
        if not isdir(dir_path):
            raise Exception(f"{dir_path} is not a valid directory.")

        abs_dir_path = abspath( dir_path )
        csv_file_name = f'{dir_path}_fp_{self.fp_rate}_size_{self.chunk_size}'
        csv_file = join(  abs_dir_path , f'{csv_file_name}.csv')
        txt_file=  join(  abs_dir_path , f'{csv_file_name}_common_stats.csv')

        commomn_stats = f'Chunk size:{self.chunk_size}\n' + f'Error rate:{self.fp_rate}'

        with open(txt_file,'w',encoding='utf8') as txtfile:
            txtfile.write(commomn_stats)

        # Headers for the csv file                
        headers = [
            'Filename', 'No_of_tokens(n)' ,'No_of_hashes(k)' , 'Filter-size(m)' , 
            'Inserted Words in dict' , 'Count_Mismatches' , 'Error in counts',
            'New words', 'False Positives', 'FP_Error'
        ]


        for current_file in listdir(abs_dir_path):

            if current_file.endswith(".html"):

                current_file_path = join(  abs_dir_path , current_file )

                self.__generate_Filter( current_file_path )

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

                #Entry for the csv file
                entry = [
                        current_file, self.n, self.k , self.m ,
                        seen_words, wrong_count , round( wrong_count / seen_words,10),
                        no_of_unseen_words , fp_count ,round(fp_count / no_of_unseen_words , 10)
                    ]
                
                if isfile( csv_file ): 
                    with open(csv_file, 'a',newline ='') as f:   
                        writer = csv.writer(f)
                        writer.writerow(entry)
                else:
                    with open(csv_file, 'w',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerow(entry)


if __name__ == '__main__':    
    obj = Tester()
    # obj.test_filter_for_file('sample.html')
    # obj.test_dir('endler')