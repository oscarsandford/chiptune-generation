# mcc_builder.py
# Functions to build and compile list (i.e. waves) together 
# as well as export audio files.

import numpy as np


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


# Given a list of tracks an an option to truncate them, 
# returns a list of each list added element-wise.
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
