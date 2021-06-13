# Sthir

<p align="center">
<img src="https://github.com/pncnmnp/sthir/blob/master/logo.png">
</p>

**Search using spectral bloom filters in static sites**

[![sthir][sthir-img]][sthir-url]
[![docs][docs-img]][docs-url]
[![python][python-img]][python-url]
[![Downloads](https://pepy.tech/badge/sthir)](https://pepy.tech/project/sthir)
[![Downloads](https://pepy.tech/badge/sthir/month)](https://pepy.tech/project/sthir/month)
[![MIT License][license-image]][license-url]

**Sthir** can create *memory efficient* search feature for your static website. Sthir is equipped with an *user friendly command-line interface*. In two steps you can build a working search page for your website!

## Description
Sthir is a library to create search functionality for your static websites. It scans your `html` pages for words and indexes these words in an efficient data structure called **Spectral Bloom Filters**. Spectral Bloom Filteres differs from regular ones as they can store counts for each hash (it can estimate, at minimum, how many times a hash was indexed). We are using an efficient base 15 decoding to compress and transfer the bloom filters at client side. Our goal can be described with a simple equation:

`Less Memory Footprint + Term Frequency Knowledge = Perfect Search Functionality for Static Sites!`

*A deployed example of our library can be found on [this blog](https://pncnmnp.github.io/blogs/search.html).*

## Installation

sthir runs on Python 3.5 or above.

Installation with [pip via PyPI](https://pypi.org/project/sthir/) for Linux, OS X and Windows:
```sh
pip install sthir
```
To check installation run the following command:
```sh
sthir -h
```
If you see the help messages without any error then the installation was successful.

## Quickstart

### Help message:
```
usage: sthir [-h] [-e ErrorRate] [-s Counter_size] [-l] [-ds] path

Creates a Spectral Bloom filter(SBF) for .html files in the specified
directory.

positional arguments:
  path             Path to source directory for creating the filter

optional arguments:
  -h, --help       show this help message and exit
  -e ErrorRate     Error_rate for the filter Range:[0.0,1.0] Default:0.01
  -s Counter_size  Size in bits of each counter in filter Range:[1,10]
                   Default:4(recommended)
  -l, --lemmetize  Enable Lemmetization
  -ds              Disable stopword removal from files (not recommended)
```

### Basic

To scan your HTML files and generate a static search webpage, use the command:
`sthir <your-path-name>`

By default, a `search.html` file, containing the static search functionality will be generated.

### Error rate
You can change the error rate of the generated Spectral Bloom Filter using:
`sthir <your-path-name> -e <error-rate>`

We recommend an error rate of `0.01`. Having a high error rate is likely to produce more false positive results (i.e. it will recommend URLs which do not contain the search word(s)).

### Counter size
By default, our counters can have a maximum count of 16 (`counter_size=4`). Counters are used by Spectral Bloom Filters to keep track of the number of times a particular hash has been indexed in the bloom filter. So by default, we keep a count till 16. However, you can chnage the counter size using: `sthir <your-path-name> -s <counter-size>`.

**Note:** 
* `counter_size` of `x` can store upto a maximum count `2^x`. For example: `counter_size` of 3, has a maximum count of `2^3` or `8`.
* As Spectral Bloom Filters are a **probabilistic** data structure, they cannot be used to accurately determine the upper bound of each word's hashes. They keep a track of the lower bound of a word's hashes (primarily using *Minimum Increment* method).

## Documentation

**Our entire documentation is available in**:
* [HTML](https://pncnmnp.github.io/sthir/)
* [PDF](https://pncnmnp.github.io/sthir/pdf/sthir.pdf)

Here is a working demo - 

![terminal-output](https://github.com/pncnmnp/sthir/blob/master/demo.gif)

## License

The library is licensed under MIT License. This project is developed by [Parth Parikh](https://github.com/pncnmnp), [Mrunank Mistry](https://github.com/fork52), and [Dhruvam Kothari](https://github.com/iotarepeat).

## Credits

* Spectral bloom filters by Saar Cohen and Yossi Matias. DOI: https://doi.org/10.1145/872757.872787
* [Writing a full-text search engine using Bloom filters](https://www.stavros.io/posts/bloom-filter-search-engine/) by Stavros Korokithakis was a major inspiration for this project.
* [Karan Lyons](https://github.com/karanlyons/) and [Sascha Droste](https://github.com/pid/) for [MurmurHash3js](https://github.com/pid/murmurHash3js). 
* [Zhuhongk](https://stackoverflow.com/users/2959866/zhuhongk) and [Nikolas](https://stackoverflow.com/users/710543/nikolas) for their code on [Is there a pure python implementation of MurmurHash?](https://stackoverflow.com/questions/13305290/is-there-a-pure-python-implementation-of-murmurhash?rq=1).
* [Data files](https://github.com/pncnmnp/sthir/tree/master/sthir/resources) are derived from the Google Web Trillion Word Corpus, as described by Thorsten Brants and Alex Franz, and distributed by the Linguistic Data Consortium. Subsets of this corpus distributed by Peter Novig. Corpus editing and cleanup by Josh Kaufman.

## Contributing

1. Fork it (<https://github.com/pncnmnp/Spectral-Bloom-Search/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[wiki]: https://github.com/yourname/yourproject/wiki
[license-image]:https://img.shields.io/badge/LICENSE-MIT-blue?style=flat
[license-url]:https://github.com/pncnmnp/sthir/blob/master/LICENSE
[sthir-img]:https://img.shields.io/badge/sthir-v0.0.1-yellow?style=flat
[sthir-url]:https://github.com/pncnmnp/sthir
[python-url]:https://www.python.org/downloads/release/python-350/
[python-img]:https://img.shields.io/badge/python-3.5-green
[docs-img]:https://img.shields.io/badge/docs-sthir--docs-orange
[docs-url]:https://pncnmnp.github.io/sthir/

## Data
https://drive.google.com/uc?id=1UpL5IPdzdPSEmv1U-ethebU_-ODKUxN0&export=download
