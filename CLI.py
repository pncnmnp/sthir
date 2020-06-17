import argparse
from pprint import pprint
from os.path import isdir,abspath
import scan

def dir_path(path):
    """Validates path to the source folder"""
    if isdir(path):
        return abspath(path) 
    else:
        raise argparse.ArgumentTypeError(f"'{abspath(path)}' is not a valid directory path.")

def error_rate_arg(val):
    """Validates the error_rate for the arg parser"""
    try:
        val = float(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{val} is not a floating-point literal")

    if val >= 0.0 and val <= 1.0:
        return val
    raise argparse.ArgumentTypeError(f"{val} not in range [0.0, 1.0]")

def chunk_size_arg(val):
    """Validates the chunk_size for the arg parser"""
    try:
        val = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{val} is not an integer value.")

    #Limit the chunk size to have only 1 to 10 bits.
    if val >= 1 and val <= 10:
        return val

    if val <= 0:
        raise argparse.ArgumentTypeError("Counter size has to be greater than zero.")
    else:
        raise argparse.ArgumentTypeError(f"{val} is too high")

def create_arg_parser():
    """Returns a well-setup argument-parser object"""
    parser = argparse.ArgumentParser(
        description='Creates a Spectral Bloom filter(SBF) for .html files in the specified directory.'
    )

    #The directory argument - posititonal argument
    parser.add_argument(
        'path', 
        type=dir_path, 
        help='Path to source directory for creating the filter'
    )

    #Error_rate
    parser.add_argument(
        '-e' ,
        type = error_rate_arg,
        metavar="ErrorRate",
        dest='error_rate', 
        default= 0.01, 
        help='Error_rate for the filter  Range:[0.0,1.0]  Default:0.01'
    )

    #Counter_size
    parser.add_argument(
        '-s' ,
        type = chunk_size_arg,
        metavar="Counter_size",
        dest='chunk_size', 
        default= 4, 
        help='Size in bits of each counter in filter Range:[1,10] Default:4(recommended)'
    )

    #Lemmetization
    parser.add_argument(
        '-l' ,'--lemmetize',
        dest='enable_lemmetization', 
        action = 'store_true',
        help='Enable Lemmetization'
    )

    #Remove stopwords
    parser.add_argument(
        '-ds',
        dest='remove_stopwords', 
        action = 'store_false',
        help='Disable stopword removal from file (not recommended)'
    )

    return parser

if __name__ == "__main__":
    parser = create_arg_parser()

    args = vars(parser.parse_args()) #Convert to dictionary

    # args- Arguments which are needed to create the SB filter.
    # pprint( args )
    scan.create_search_page(args["path"], output_file="search.html", false_positive=args["error_rate"], chunk_size=args["chunk_size"], remove_stopwords=args["remove_stopwords"])