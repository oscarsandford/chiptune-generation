# mcc_waves.py
# Functions to create and manipulate waves, envelopes, and frequencies.

from time import time
import numpy as np


# Stupid thing.
RTTTL2MIDI = {'c1': 24, 'c#1': 25, 'd1': 26, 'd#1': 27, 'e1': 28, 'f1': 29, 'f#1': 30, 'g1': 31, 'g#1': 32, 'a1': 33, 'a#1': 34, 'b1': 35, 
			'c2': 36, 'c#2': 37, 'd2': 38, 'd#2': 39, 'e2': 40, 'f2': 41, 'f#2': 42, 'g2': 43, 'g#2': 44, 'a2': 45, 'a#2': 46, 'b2': 47, 
			'c3': 48, 'c#3': 49, 'd3': 50, 'd#3': 51, 'e3': 52, 'f3': 53, 'f#3': 54, 'g3': 55, 'g#3': 56, 'a3': 57, 'a#3': 58, 'b3': 59, 
			'c4': 60, 'c#4': 61, 'd4': 62, 'd#4': 63, 'e4': 64, 'f4': 65, 'f#4': 66, 'g4': 67, 'g#4': 68, 'a4': 69, 'a#4': 70, 'b4': 71, 
			'c5': 72, 'c#5': 73, 'd5': 74, 'd#5': 75, 'e5': 76, 'f5': 77, 'f#5': 78, 'g5': 79, 'g#5': 80, 'a5': 81, 'a#5': 82, 'b5': 83, 
			'c6': 84, 'c#6': 85, 'd6': 86, 'd#6': 87, 'e6': 88, 'f6': 89, 'f#6': 90, 'g6': 91, 'g#6': 92, 'a6': 93, 'a#6': 94, 'b6': 95, 
			'c7': 96, 'c#7': 97, 'd7': 98, 'd#7': 99, 'e7': 100, 'f7': 101, 'f#7': 102, 'g7': 103, 'g#7': 104, 'a7': 105, 'a#7': 106, 'b7': 107}

def _midi_to_freq(pitch:float) -> float:
	"""
	A simple function to change a MIDI note to a frequency.
	"""
	return 440*(2**((pitch-69)/12.0))


def triangle_wave(freq:float, dur:float=1.0, sr:float=44100) -> np.array:
	"""
	Approximate a triangle wave with 4 harmonics based on the equation 
	here: https://en.wikipedia.org/wiki/Triangle_wave#Harmonics.	
	"""
	# f0 = _midi_to_freq(pitch)
	t = np.arange(0, dur, 1.0/sr)
	x = np.zeros(t.shape[0])
	for i in range(4):
		n = 2*i + 1
		x += ((-1)**i)*(n**(-2))*(np.sin(2*np.pi*freq*n*t))
	return (8/(np.pi**2)) * x


def square_wave(freq:float, dur:float=1.0, sr:float=44100) -> np.array:
	"""
	A function for square waves, a typical waveform used for NES/SEGA-type sounds.
	The equations can be found here: https://en.wikipedia.org/wiki/Square_wave
	"""
	# f = _midi_to_freq(pitch)
	t = np.arange(0, dur, 1.0/sr)
	return 2 * (2*np.floor(freq*t) - np.floor(2*freq*t)) + 1


def adsr_envelope(dur:float, props:list=[0.1,0.3,0.5], sr:int=44100) -> np.array:
	"""
	Creates an ASDR (attack-decay-sustain-release) envelope for a given duration 
	with a sort of fade-in and fade-out. Customize the ASDR via the props param. 
	The release time is the remaining duration. 
	For example, if props=[0.1, 0.2, 0.5] and duration=3.0, then
	 - attack goes from 0-0.3 seconds (+0.3 seconds)
	 - decay goes from 0.3-0.9 seconds (+0.6 seconds)
	 - sustain goes from 0.9-2.4 seconds (+1.5 seconds)
	 - release goes from 2.4-3.0 seconds (+0.6 seconds)

	props[0] : proportion of time for attack stage
	props[1] : proportion of time for decay stage
	props[2] : proportion of time for sustain stage
	"""
	assert sum(props) <= 1.0 and all(p > 0 for p in props), "MCC: Each time proportion must be non-negative and sum not over 1.0."

	n_attack = 0
	t_decay = props[0] * dur
	t_sustain = t_decay + (props[1]*dur)
	t_release = t_sustain + (props[2]*dur)
	
	n_decay = int(t_decay * sr)
	n_sustain = int(t_sustain * sr)
	n_release = int(t_release * sr)
	n_end = int(dur*sr)
	
	ampl_attack = 1.0
	ampl_sustain = 0.3
	ampl_end = 0.01
	ampl = np.zeros(n_end)
	
	ampl[n_attack:n_decay] = np.geomspace(0.1, ampl_attack, n_decay-n_attack)
	ampl[n_decay:n_sustain] = np.geomspace(ampl_attack, ampl_sustain, n_sustain-n_decay)
	ampl[n_sustain:n_release] = ampl_sustain
	ampl[n_release:] = np.geomspace(ampl_sustain, ampl_end, n_end-n_release)
	
	return ampl


def _split_note(note_st:str) -> tuple:
	"""
	Given a RTTTL formatted note, return 
	a pair: duration and pitch.
	"""
	for i, c in enumerate(note_st):
		if c in "abcdefgp":
			d, p = note_st[:i], note_st[i:]
			return 1/4 if len(d) == 0 else 1/int(d), p
	raise Exception("MCC: Bad note.")
		

def notes_to_waveform(notes:list, bpm:float, time_signature:int=4, wave_function=square_wave, do_envl:bool=True) -> np.array:
	"""
	NEW!
	A new method for turning a string of notes (based on this spec http://merwin.bespin.org/t4a/specs/nokia_rtttl.txt) 
	into a playable waveform melody. 
	
	:param: notes, a list of notes in RTTTL.
	:param: bpm, defines the tempo of the melody. 
	:param: time_signature, the time signature defaults to 4/4 time. Set as 3 for 3/4, 5 for 5/4, etc.
	:param: wave_function, the type of waves to generate for these notes.
	:param: do_envl, flag to make the note sound smoother with ADSR envelope.

	based on this:
	https://flothesof.github.io/gameboy-sounds-in-python.html#A-function-that-parses-the-melody-and-generates-a-sound
	"""
	measure_len = time_signature * 60 / bpm
	waveform = np.zeros((0,))
	for note in notes.split(","):
		duration, pitch = _split_note(note)

		# Dotted note: extends duration by half. Reformat pitch string.
		if "." in pitch:
			duration *= 1.5
			pitch = pitch.replace(".", "")
		duration *= measure_len

		# Pause (p) indicates a rest, i.e. frequency 0.
		if "p" in pitch:
			frequency = 0.
		else:
			if pitch[-1] in [str(i) for i in range(1,9)]:
				frequency = _midi_to_freq(RTTTL2MIDI[pitch])
			else: # Default to 5th octave.
				frequency = _midi_to_freq(RTTTL2MIDI[pitch+"5"])
		
		wave = wave_function(frequency, duration)

		if do_envl:
			envl = adsr_envelope(duration)
			wavelen = min(len(wave), len(envl))
			wave = wave[:wavelen] * envl[:wavelen]
		
		waveform = np.hstack((waveform, wave))

	return waveform
	
"""
!!!
The functions below work for a deprecated way to create sound waves from notes of a specific format in a track.
"""

def _add_wave(waves: list, wave: list, idx: int):
	"""
	Add a wave to a list of waves, starting at index idx. 
	If the waves list is smaller, extend the waves list with 0.0's. 
	This operation is done in-place and does not return a new list.
	"""
	if len(waves) < len(wave):
		waves += [0.]*(len(wave)-len(waves))
	waves[idx:len(wave)] = wave


def create_track_wave(track:list, wave_function=square_wave, tempo:int=1000, envl:bool=False) -> list:
	"""
	Creates a wave for a given track, with the option to use different wave functions and envelope or not.

	`track`
		A list of notes.
	`wave_function`
		A function used to generate a sound wave for each note (the default is a triangle wave).
	`tempo`
		A numerical value used when determining the length of the note. TODO: HARDCODED - THIS MUST BE REWORKED.
	`envl`
		Whether to apply the default envelope to the wave.
	"""
	track_waves = []
	ptr = 0
	for i, note in enumerate(track):
		if note[3]:
			for n in track[i:]:
				if n[0] == note[0] and not n[3]:
					ntime = n[2]
					break
		else:
			ntime = 0

		note_wave = wave_function(note[0], dur=ntime/tempo)
		if envl:
			envl_wave = adsr_envelope(ntime/tempo)
			wavelen = min(len(note_wave), len(envl_wave))
			note_wave = note_wave[:wavelen] * envl_wave[:wavelen]

		_add_wave(track_waves, note_wave, ptr)
		ptr += len(note_wave)
	
	return track_waves


def create_all_track_waves(tracks:list, wave_function=square_wave, tempo:int=1000, envl:bool=False) -> list:
	"""
	Input a list of lists. Create wave for all tracks.
	"""
	track_waves = []
	for track in tracks:
		if len(track) > 0:
			wave = create_track_wave(track, wave_function, tempo, envl)
			track_waves.append(wave)
	return track_waves
