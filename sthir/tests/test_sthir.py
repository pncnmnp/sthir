import unittest
from sthir.spectral_bloom_filter import Hash_Funcs , Spectral_Bloom_Filter


class Test_Hashing(unittest.TestCase):
    def test_hashes1(self):
        k , m = 3 , 200
        hash_obj = Hash_Funcs(k , m)
        self.assertEqual( [133, 193, 69],  hash_obj.get_hashes("dogs"))

    def test_hashes2(self):
        k , m = 5 , 100
        hash_obj = Hash_Funcs(k , m)
        self.assertEqual([66, 78, 4, 86, 26],   hash_obj.get_hashes("cats"))
    

class Test_SBF(unittest.TestCase):
    def test_SBF(self):
        SBF = Spectral_Bloom_Filter()

        expected = (480 , 3)
        actual = SBF.optimal_m_k(100, 0.1)
        self.assertEqual( expected,  actual )

if __name__ == '__main__':
    unittest.main()

    
    # SBF = Spectral_Bloom_Filter()

    # print( ) 
