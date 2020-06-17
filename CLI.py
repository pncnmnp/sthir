import argparse

def error_rate_arg(val):
    try:
        val = float(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{val} is not a floating-point literal")

    if val >= 0.0 and val <= 1.0:
        return val
    raise argparse.ArgumentTypeError(f"{val} not in range [0.0, 1.0]")

def chunk_size_arg(val):
    try:
        val = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{val} is not an integer.")

    #Limit the chunk size to have only 1 to 10 bits.
    if val >= 1 and val <= 10:
        return val

    if val <= 0:
        raise argparse.ArgumentTypeError("Counter size has to be greater than zero.")

    raise argparse.ArgumentTypeError(f"{val} is too high")

def create_arg_parser():


    parser = argparse.ArgumentParser(
        description='Creates a Spectral Bloom filter(SBF) for .html files in the specified directory.'
    )

    #The directory argument - posititonal argument
    parser.add_argument(
        'dir', 
        type=str, 
        help='Source directory for creating the filter'
    )

    #Error_rate
    parser.add_argument(
        '-e' ,
        type = error_rate_arg,
        metavar="ErrorRate",
        dest='error_rate', 
        default= 0.01, 
        help='Error_rate for the filter  Range:[ 0.0 , 1.0 ]  Default=0.1.'
    )

    #Counter_size
    parser.add_argument(
        '-s' ,
        type = chunk_size_arg,
        metavar="Counter_size",
        dest='chunk_size', 
        default= 4, 
        help='Size in bits of each counter in filter. Default=4(recommended). Range=[1,10]'
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
    '-d',
        dest='remove_stopwords', 
        action = 'store_false',
        help='Disable stopword removal from file (not recommended)'
    )

    return parser


if __name__ == "__main__":
    parser = create_arg_parser()
    args = vars(parser.parse_args())

    #Arguments which are important
    print( args )
