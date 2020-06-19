# Sthir

<p align="center">
<img src="https://github.com/pncnmnp/sthir/blob/master/logo.png">
</p>

**Search using spectral bloom filters in static sites**

[![sthir][sthir-img]][sthir-url]
[![docs][docs-img]][docs-url]
[![python][python-img]][python-url]
[![MIT License][license-image]][license-url]

**Sthir** can create *memory efficient* search feature for your static website. Sthir is equipped with an *user friendly command-line interface*. In two steps you can build a working search page for your website!

## Description
Sthir is a library to create search functionality for your static websites. It scans your `html` pages for words and indexes these words in an efficient data structure called **Spectral Bloom Filters**. Spectral Bloom Filteres differs from regular ones as they can store counts for each hash (it can estimate, at minimum, how many times a hash was indexed). We are using an efficient base 15 decoding to compress and transfer the bloom filters at client side. Our goal can be described with a simple equation:

`Less Memory Footprint + Term Frequency Knowledge = Perfect Search Functionality for Static Sites!`

## Installation

sthir runs on Python 3.5 or above.

Installation with pip via PyPI for OS X , Linux and Windows:
```sh
pip install sthir
```
To check installation run the following command:
```sh
sthir -h
```
If you see the help messages without any error then the installation was successful.

## Documentation
Here is a working demo - 

![terminal-output](https://github.com/pncnmnp/sthir/blob/master/demo.gif)

**Our entire documentation is available in**:
* [PDF](https://github.com/pncnmnp/sthir/blob/master/docs/build/latex/sthir.pdf)
* [HTML](https://github.com/pncnmnp/sthir/tree/master/docs/build/html)

## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
```

## Release History

* 0.2.1
    * CHANGE: Update docs (module code remains unchanged)
* 0.2.0
    * CHANGE: Remove `setDefaultXYZ()`
    * ADD: Add `init()`
* 0.1.1
    * FIX: Crash when calling `baz()` (Thanks @GenerousContributorName!)
* 0.1.0
    * The first proper release
    * CHANGE: Rename `foo()` to `bar()`
* 0.0.1
    * Work in progress

## Meta

Your Name – [@YourTwitter](https://twitter.com/dbader_org) – YourEmail@example.com

Distributed under the XYZ license. See ``LICENSE`` for more information.

[https://github.com/pncnmnp/Spectral-Bloom-Search/blob/master/LICENSE](LICENSE)

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
[docs-url]:https://github.com/pncnmnp/sthir/
