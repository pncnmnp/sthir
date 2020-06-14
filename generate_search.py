import base64
from typing import Iterable


def gen_chunks(string: str,
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


def base2p15_encode(bit_string: str) -> str:
    base2p15 = ""
    offset = 0xa1

    # Padding bit_string if not multiple of 15
    padding_bits = (15 - len(bit_string) % 15) % 15
    bit_string += "0" * padding_bits
    base2p15 += hex(padding_bits)[2:]

    assert len(bit_string) % 15 == 0
    # Encode remaining data
    for chunk in gen_chunks(bit_string, 15):
        character = chr(int(chunk, 2) + offset)
        base2p15 += character

    return base2p15


def base2p15_decode(base2p15: str) -> str:
    bit_string = ""
    offset = 0xa1
    padding = int(base2p15[0], 16)
    for character in base2p15[1:-1]:
        character = ord(character) - offset
        bits = bin(character)[2:].zfill(15)
        bit_string += bits

    character = ord(base2p15[-1]) - offset
    bits = bin(character)[2:].zfill(15)[:15 - padding]
    bit_string += bits
    return bit_string


def base2p15_get_range(base2p15: str, start: int, end: int) -> str:
    assert start < end
    assert start >= 0
    assert end < (len(base2p15) - 1) * 15 - int(base2p15[0], 16) + 1
    range_str = base2p15[1:][start // 15:(end // 15) + 1]
    end_pad = hex(15 - end % 15)[2:]
    start_pad = start % 15
    d = base2p15_decode(end_pad + range_str)[start_pad:]
    return d
