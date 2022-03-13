# mcc_builder.py
# Functions to build and compile list (i.e. waves) together 
# as well as export audio files.

import numpy as np
from scipy.io.wavfile import write

def _min_len_nonzero(lili: list) -> int:
	"""
	Input a list of lists.
	Return the length of the track with the minimum non-zero length.
	"""
	minlen = np.inf
	for li in lili:
		if len(li) < minlen:
			minlen = len(li)
	return minlen


def combine_tracks(tracks: list, truncate:bool=True) -> list:
	"""
	Input a list of lists (tracks). Combine each track by element-wise adding each list. 
	Truncate each track so they have the same length. Return a single list of floating point numbers.
	"""
	assert len(tracks) > 0 and all(len(t) > 0 for t in tracks), "MCC: Each track must be non-empty."
	if truncate:
		l = _min_len_nonzero(tracks)
		tracks = [t[:l] for t in tracks]
	
	combined = np.zeros(len(tracks[0]))
	for t in tracks:
		combined += t
	return combined


def join(*args):
	"""
	Do the "+" operation on a undefined number of args of the same type.
	Useful for concatenating many strings together.
	"""
	return args[0] + join(*args[1:]) if len(args) > 1 else args[0]


def export_to_wav(track: list, srate: int, name):
	"""
	Input a list of track (number list), sampling rate and the name of the file.
	Save the input as .wav file.
	"""
	assert len(track) > 0
	write('../out/' + name + '.wav', srate, track.astype(np.uint8))
