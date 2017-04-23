MyCrypt Version 0.0.3
============
This is a application for:
1. encrypt and decrypt files
2. rename and delete files and folders
3. copy, cut and paste files and folders

Installation
============
Before you run it, please install the following packages.
Some packages in the "MyCrypt/vendor".
To install:
1. python-setuptools
2. tornado
3. python-dateutil
4. pyyaml
5. psutil
6. cython
7. tea (a python and cython module for encrypt and decrypt)

In Windows, you can install mingw, cython and numpy, then can install tea(use C extension),
or, if you don't want to install mingw, cython and numpy, you can install tea(use pure python),
tea packages will detect if cython has been installed and then install tea with it or not.
Without cython and numpy, encrypt and decrypt speed will slow down.

In Linux, you just install cython and numpy, then install tea.



