import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sthir", 
    version="0.0.2",
    author="Parth Parikh, Dhruvam Kothari,Mrunank Mistry",
    author_email="mrunankmistry52@gmail.com",
    description="A package for creating Spectral Bloom filters for static sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pncnmnp/Spectral-Bloom-Search",
    packages=setuptools.find_packages(),
    install_requires=[
          'nltk','bs4','newspaper3k','lxml',
          'requests' ,'pytest'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    entry_points ={ 
        'console_scripts': [ 
            'sthir = sthir.CLI:sthir_arg_parser'
        ] 
    }, 
    zip_safe=False,
    keywords = ['Spectral Bloom Filters','Static Website','Searching']
)