# mcc_waves.py
# Functions to create and manipulate waves, envelopes, and frequencies.

import numpy as np


def _midi_to_freq(pitch:float) -> float:
	"""
	A simple function to change a MIDI note to a frequency.
	"""
	return 440*(2**((pitch-69)/12.0))


def triangle_wave(pitch:float, dur:float=1.0, sr:float=44100) -> np.array:
	"""
	Approximate a triangle wave with 4 harmonics based on the equation 
	here: https://en.wikipedia.org/wiki/Triangle_wave#Harmonics.	
	"""
	f0 = _midi_to_freq(pitch)
	t = np.arange(0, dur, 1.0/sr)
	x = np.zeros(t.shape[0])
	for i in range(4):
		n = 2*i + 1
		x += ((-1)**i)*(n**(-2))*(np.sin(2*np.pi*f0*n*t))
	return (8/(np.pi**2)) * x


def square_wave(pitch:float, dur:float=1.0, sr:float=44100) -> np.array:
	"""
	A function for square waves, a typical waveform used for NES/SEGA-type sounds.
	The equations can be found here: https://en.wikipedia.org/wiki/Square_wave
	"""
	f = _midi_to_freq(pitch)
	t = np.arange(0, dur, 1.0/sr)
	return 2 * (2*np.floor(f*t) - np.floor(2*f*t)) + 1


def adsr_envelope(dur:float, props:list=[0.1,0.2,0.5], sr:int=44100) -> np.array:
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
