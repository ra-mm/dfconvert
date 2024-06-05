# dfconvert

[![PyPI version](https://badge.fury.io/py/dfconvert.svg)](https://badge.fury.io/py/dfconvert)
[![Build Status](https://travis-ci.org/dataflownb/dfconvert.svg?branch=beta-update)](https://travis-ci.org/dataflownb/dfconvert)

This library allows the conversion of Dataflow notebooks into their IPykernel equivalents. There is no guarantee made that the Notebook that enters will be as efficient as the notebook in the Dfkernel but it will perform in the same way.

A topological sort if also applied to the Notebook to ensure that it can be ran top down.

It relies on IPython core methods for some of the translation process so some magic and system commands may be translated into their IPython equivalent.

## Installation Instructions

1. cd to outer `dfconvert` that contains `setup.py`.
2. `pip install .`


### Usage
By installing the package, you will have a new option "Export as IPython Notebook" available in the toolbar interface of the Jupyter Notebook.

Optionally the package can also be called by the use of
```
from dfconvert.export import convert_dfnotebook
file_name = 'mynotebook.ipynb'
nb = nbformat.read(file_name,nbformat.NO_CONVERT)
new_file_name = 'mynewnotebook.ipynb'
convert_dfnotebook(nb, in_fname=file_name, out_fname=new_file_name)
```

This will create a notebook with `out_fname` as an ipykernel compatible notebook if `out_fname` is not set then a file will be created with `file_name` that includes a `_dfpy` before the extension to ensure that files do not become overwritten. 
