import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sthir", 
    version="0.0.1",
    author="Parth Parikh, Dhruvam Kothari,Mrunank Mistry",
    author_email="mrunankmistry52@gmail.com",
    description="A package for creating Spectral Bloom filters for static sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pncnmnp/Spectral-Bloom-Search",
    packages=setuptools.find_packages(),
    install_requires=[
          'nltk', 'bitarray' ,'bs4','newspaper3k','lxml',
          'requests'
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
            'sthir = sthir.CLI:create_arg_parser'
        ] 
    }, 
    zip_safe=False
)