# mcc_waves.py
# Functions to create and manipulate waves, envelopes, and frequencies.

import numpy as np
from scipy import signal


# A mapping for RTTTL notes to MIDI notes. 
# Opposite mapping for MIDI2RTTTL in mcc_parser module.
# Based on this: https://en.wikipedia.org/wiki/Piano_key_frequencies#List
RTTTL2MIDI = {'c1': 24, 'c#1': 25, 'd1': 26, 'd#1': 27, 'e1': 28, 'f1': 29, 'f#1': 30, 'g1': 31, 'g#1': 32, 'a1': 33, 'a#1': 34, 'b1': 35, 
			'c2': 36, 'c#2': 37, 'd2': 38, 'd#2': 39, 'e2': 40, 'f2': 41, 'f#2': 42, 'g2': 43, 'g#2': 44, 'a2': 45, 'a#2': 46, 'b2': 47, 
			'c3': 48, 'c#3': 49, 'd3': 50, 'd#3': 51, 'e3': 52, 'f3': 53, 'f#3': 54, 'g3': 55, 'g#3': 56, 'a3': 57, 'a#3': 58, 'b3': 59, 
			'c4': 60, 'c#4': 61, 'd4': 62, 'd#4': 63, 'e4': 64, 'f4': 65, 'f#4': 66, 'g4': 67, 'g#4': 68, 'a4': 69, 'a#4': 70, 'b4': 71, 
			'c5': 72, 'c#5': 73, 'd5': 74, 'd#5': 75, 'e5': 76, 'f5': 77, 'f#5': 78, 'g5': 79, 'g#5': 80, 'a5': 81, 'a#5': 82, 'b5': 83, 
			'c6': 84, 'c#6': 85, 'd6': 86, 'd#6': 87, 'e6': 88, 'f6': 89, 'f#6': 90, 'g6': 91, 'g#6': 92, 'a6': 93, 'a#6': 94, 'b6': 95, 
			'c7': 96, 'c#7': 97, 'd7': 98, 'd#7': 99, 'e7': 100, 'f7': 101, 'f#7': 102, 'g7': 103, 'g#7': 104, 'a7': 105, 'a#7': 106, 'b7': 107}

def _midi_to_freq(pitch:float) -> float:
	"""
	A simple function to change a MIDI pitch to a frequency.
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


def sawtooth_wave(freq:float, dur:float=1.0, sr:float=44100) -> np.array:
	"""
	Sawtooth wave seem to combine triangle and square waves, 
	with a leading slope, and the abrubt drop of a square wave.
	https://en.wikipedia.org/wiki/Sawtooth_wave
	Shoutout to scipy! :D
	"""
	t = np.arange(0, dur, 1.0/sr)
	return signal.sawtooth(2 * freq * np.pi * t)


def adsr_envelope(duration:float, props:list=[0.1,0.3,0.5], sr:int=44100) -> np.array:
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
	t_decay = props[0] * duration
	t_sustain = t_decay + (props[1]*duration)
	t_release = t_sustain + (props[2]*duration)
	
	n_decay = int(t_decay * sr)
	n_sustain = int(t_sustain * sr)
	n_release = int(t_release * sr)
	n_end = int(duration*sr)
	
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
			return (1/4, p) if len(d) == 0 else (1/int(d), p)
	raise Exception(f"MCC: {note_st} was a bad note.")


def notes_to_waveform(notes:list, bpm:float, time_signature:int=4, octave:int=5, wave_function=square_wave, do_envl:bool=True) -> np.array:
	"""
	A function for turning a string of RTTTL notes (based on this spec http://merwin.bespin.org/t4a/specs/nokia_rtttl.txt) 
	into a playable waveform melody. 
	
	:param: notes, a list of notes in RTTTL.
	:param: bpm, defines the tempo of the melody. 
	:param: time_signature, the time signature defaults to 4/4 time. Set as 3 for 3/4, 5 for 5/4, etc.
	:param: octave, the octave to default to if no octave is specfied on a note.
	:param: wave_function, the type of waves to generate for these notes.
	:param: do_envl, flag to make the note sound smoother with ADSR envelope.

	This function was writte based on this:
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
			else:
				frequency = _midi_to_freq(RTTTL2MIDI[f"{pitch}{octave}"])
		
		# TODO (opt): cache or record waveforms of RTTTL notes already converted 
		# to waveforms so that we don't need to run this expensive function 
		# a lot - the result should make overall computation faster.
		wave = wave_function(frequency, duration)

		if do_envl:
			envl = adsr_envelope(duration)
			wavelen = min(len(wave), len(envl))
			wave = wave[:wavelen] * envl[:wavelen]
		
		waveform = np.hstack((waveform, wave))

	return waveform
