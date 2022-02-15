# /src

Source code for our implementation will be stored here.

## Overview
* `/data`: The storage for input music files, including MIDI, MP3, WAV, MusicXML.
* `/out`: Used as a bin for all types of output files.
* `/modules`: Location for Python module source files.

The idea is to place key driver source code files and documentation at the source root, and distribute everything else as above. This paradigm is likely to evolve as the project progresses.

## Setup
Install Python3, pip, Jupyter Notebook. 

### Virtual Environment (optional; recommended)
I recommend using a virtual environment with [venv](https://docs.python.org/3/library/venv.html) to avoid polluting your global pip environment. 
In this `/src` directory:
```sh
python3 -m venv envmcc
```
Activate and deactivate the environment like so:
```sh
source envmcc/bin/activate
deactivate
```
While your virtual env is active, installing Python packages with pip will add them to the environment.

### Install Packages
Install required packages with 
```
pip install -r requirements.txt
```
