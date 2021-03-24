#https://stackoverflow.com/questions/13305290/is-there-a-pure-python-implementation-of-murmurhash?rq=1

from functools import lru_cache


@lru_cache(10000)
def murmur3_x86_32(key, seed = 0):
    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    length = len(key)
    h1 = seed
    roundedEnd = (length & 0xfffffffc)  # round down to 4 byte block
    for i in range(0, roundedEnd, 4):
      # little endian load order
      k1 = (ord(key[i]) & 0xff) | ((ord(key[i + 1]) & 0xff) << 8) | \
           ((ord(key[i + 2]) & 0xff) << 16) | (ord(key[i + 3]) << 24)
      k1 *= c1
      k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17) # ROTL32(k1,15)
      k1 *= c2

      h1 ^= k1
      h1 = (h1 << 13) | ((h1 & 0xffffffff) >> 19)  # ROTL32(h1,13)
      h1 = h1 * 5 + 0xe6546b64

    # tail
    k1 = 0

    val = length & 0x03
    if val == 3:
        k1 = (ord(key[roundedEnd + 2]) & 0xff) << 16
    # fallthrough
    if val in [2, 3]:
        k1 |= (ord(key[roundedEnd + 1]) & 0xff) << 8
    # fallthrough
    if val in [1, 2, 3]:
        k1 |= ord(key[roundedEnd]) & 0xff
        k1 *= c1
        k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17)  # ROTL32(k1,15)
        k1 *= c2
        h1 ^= k1

    # finalization
    h1 ^= length

    # fmix(h1)
    h1 ^= ((h1 & 0xffffffff) >> 16)
    h1 *= 0x85ebca6b
    h1 ^= ((h1 & 0xffffffff) >> 13)
    h1 *= 0xc2b2ae35
    h1 ^= ((h1 & 0xffffffff) >> 16)

    return h1 & 0xffffffff

# if __name__ == '__main__':
#     for i in range(3):
#         print( murmur3_x86_32('Mrunank' , i) )
