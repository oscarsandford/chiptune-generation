# mcc_builder.py
# Functions to build and compile list (i.e. waves) together 
# as well as export audio files.

import numpy as np
from scipy.io.wavfile import write


def combine_tracks(tracks: list) -> np.array:
	"""
	Takes a list of tracks, each track in its waveform. Add them elementwise.
	"""
	maxlen = max(list(map(len, tracks)))
	combined = np.zeros(maxlen)
	for t in tracks:
		t = np.pad(t, (0,maxlen-t.shape[0]))
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
