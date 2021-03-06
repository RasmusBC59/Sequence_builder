# sequencebuilder
<p align="center">
  <img src="https://img.shields.io/static/v1?style=for-the-badge&label=code-status&message=Caution!&color=red"/>
  <img src="https://img.shields.io/static/v1?style=for-the-badge&label=initial-commit&message=Rasmus&color=inactive"/>
    <img src="https://img.shields.io/static/v1?style=for-the-badge&label=maintainer&message=cQED&color=inactive"/>
</p>
# Description
Package for building broadbean sequences and measure with the Alazar card
# Installation

# Usage

## Running the tests

If you have gotten 'sequencebuilder' from source, you may run the tests locally.

Install `sequencebuilder` along with its test dependencies into your virtual environment by executing the following in the root folder

```bash
$ pip install .
$ pip install -r test_requirements.txt
```

Then run `pytest` in the `tests` folder.

## Building the documentation

If you have gotten `sequencebuilder` from source, you may build the docs locally.

Install `sequencebuilder` along with its documentation dependencies into your virtual environment by executing the following in the root folder

```bash
$ pip install .
$ pip install -r docs_requirements.txt
```

You also need to install `pandoc`. If you are using `conda`, that can be achieved by

```bash
$ conda install pandoc
```
else, see [here](https://pandoc.org/installing.html) for pandoc's installation instructions.

Then run `make html` in the `docs` folder. The next time you build the documentation, remember to run `make clean` before you run `make html`.
