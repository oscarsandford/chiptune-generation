# mcc_parser.py
# Functions to parse Midi files.

from mido import MidiFile, tempo2bpm

MIDI2RTTTL = {
	24: 'c1', 25: 'c#1', 26: 'd1', 27: 'd#1', 28: 'e1', 29: 'f1', 30: 'f#1', 31: 'g1', 32: 'g#1', 33: 'a1', 
	34: 'a#1', 35: 'b1', 36: 'c2', 37: 'c#2', 38: 'd2', 39: 'd#2', 40: 'e2', 41: 'f2', 42: 'f#2', 43: 'g2', 
	44: 'g#2', 45: 'a2', 46: 'a#2', 47: 'b2', 48: 'c3', 49: 'c#3', 50: 'd3', 51: 'd#3', 52: 'e3', 53: 'f3', 
	54: 'f#3', 55: 'g3', 56: 'g#3', 57: 'a3', 58: 'a#3', 59: 'b3', 60: 'c4', 61: 'c#4', 62: 'd4', 63: 'd#4', 
	64: 'e4', 65: 'f4', 66: 'f#4', 67: 'g4', 68: 'g#4', 69: 'a4', 70: 'a#4', 71: 'b4', 72: 'c5', 73: 'c#5', 
	74: 'd5', 75: 'd#5', 76: 'e5', 77: 'f5', 78: 'f#5', 79: 'g5', 80: 'g#5', 81: 'a5', 82: 'a#5', 83: 'b5', 
	84: 'c6', 85: 'c#6', 86: 'd6', 87: 'd#6', 88: 'e6', 89: 'f6', 90: 'f#6', 91: 'g6', 92: 'g#6', 93: 'a6', 
	94: 'a#6', 95: 'b6', 96: 'c7', 97: 'c#7', 98: 'd7', 99: 'd#7', 100: 'e7', 101: 'f7', 102: 'f#7', 
	103: 'g7', 104: 'g#7', 105: 'a7', 106: 'a#7', 107: 'b7'
}

INSTRUMENTS = [
	'Acoustic Grand Piano','Bright Acoustic Piano','Electric Grand Piano','Honky-tonk Piano','Electric Piano 1','Electric Piano 2','Harpsichord',
	'Clavi','Celesta','Glockenspiel','Music Box','Vibraphone','Marimba','Xylophone','Tubular Bells','Dulcimer','Drawbar Organ','Percussive Organ',
	'Rock Organ','Church Organ','Reed Organ','Accordion','Harmonica','Tango Accordion','Acoustic Guitar (nylon)','Acoustic Guitar (steel)',
	'Electric Guitar (jazz)','Electric Guitar (clean)','Electric Guitar (muted)','Overdriven Guitar','Distortion Guitar','Guitar harmonics',
	'Acoustic Bass','Electric Bass (finger)','Electric Bass (pick)','Fretless Bass','Slap Bass 1','Slap Bass 2','Synth Bass 1','Synth Bass 2',
	'Violin','Viola','Cello','Contrabass','Tremolo Strings','Pizzicato Strings','Orchestral Harp','Timpani','String Ensemble 1','String Ensemble 2',
	'SynthStrings 1','SynthStrings 2','Choir Aahs','Voice Oohs','Synth Voice','Orchestra Hit','Trumpet','Trombone','Tuba','Muted Trumpet','French Horn',
	'Brass Section','SynthBrass 1','SynthBrass 2','Soprano Sax','Alto Sax','Tenor Sax','Baritone Sax','Oboe','English Horn','Bassoon','Clarinet','Piccolo',
	'Flute','Recorder','Pan Flute','Blown Bottle','Shakuhachi','Whistle','Ocarina','Lead 1 (square)','Lead 2 (sawtooth)','Lead 3 (calliope)','Lead 4 (chiff)',
	'Lead 5 (charang)','Lead 6 (voice)','Lead 7 (fifths)','Lead 8 (bass + lead)','Pad 1 (new age)','Pad 2 (warm)','Pad 3 (polysynth)','Pad 4 (choir)',
	'Pad 5 (bowed)','Pad 6 (metallic)','Pad 7 (halo)','Pad 8 (sweep)','FX 1 (rain)','FX 2 (soundtrack)','FX 3 (crystal)','FX 4 (atmosphere)','FX 5 (brightness)',
	'FX 6 (goblins)','FX 7 (echoes)','FX 8 (sci-fi)','Sitar','Banjo','Shamisen','Koto','Kalimba','Bag pipe','Fiddle','Shanai','Tinkle Bell','Agogo','Steel Drums',
	'Woodblock','Taiko Drum','Melodic Tom','Synth Drum','Reverse Cymbal','Guitar Fret Noise','Breath Noise','Seashore','Bird Tweet','Telephone Ring','Helicopter',
	'Applause','Gunshot'
]


def program_to_instrument(program:int) ->  str:
	"""
	Maps a program number to a specific instrument under 
	the INSTRUMENTS lookup.
	TODO: maybe don't always have this table in memory? 
	Only load it in when needed, and then keep it persistent.
	"""
	assert 1 <= program <= 128, "MCC: Bad input."
	return INSTRUMENTS[program - 1]


def open_midi(filepath:str) -> MidiFile:
	"""
	Return the MidiFile object given its filename.
	"""
	assert ".mid" in filepath, "MCC: Cannot open non-MIDI file."
	return MidiFile(filepath, clip=True)


def get_note_lengths(file_info: list) -> dict:
	bpm = file_info[2][1]
	notes = {"whole note": 240 / bpm, "half note": 120 / bpm, "quarter note": 60 / bpm, "eighth note": 30 / bpm,
			 "sixteenth note": 15 / bpm}
	return notes
"""
currently, this implementation only works assuming the format of the midi files we've seen so far is the usual, ie. the 
time signature is first, then the key signature, then the tempo is set. This is why if you pass it the list of extracted info
from the midi file, the tempo should always be the 2nd entry of the 3rd list in the input
"""


def extract_midi_info(meta_messages: list) -> list:
	"""
	Input the first track of a MIDI file containing meta messages
	with key info such as timestamps for tempo change.
	Return a dictionary of relevant information for a MIDI file.
	"""
	MidiInfo = []
	for msg in meta_messages:
		if msg.type == "time_signature":
			info = (msg.type, msg.numerator, msg.denominator)
			MidiInfo.append(info)
		if msg.type == "key_signature":
			info = (msg.type, msg.key)
			MidiInfo.append(info)
		if msg.type == 'set_tempo':
			info = (msg.type, tempo2bpm(msg.tempo), msg.time)
			MidiInfo.append(info)
	return MidiInfo


def extract_midi_tracks(mid_tracks:list) -> list:
	"""
	Iterate over a list of tracks and create a list for each
	track containing the notes in each track, preserving the order.

	Each note is stored as a 4-tuple:
		(
			note: int, the note key on a piano
			velocity: int, the strength of the key where 0 means the note is off, or a rest
			time: int, the wait time between the last and current note or operation, so the
				duration of a note is the sum of time in between the two nearest messages
				containing the same note
			on/off: bool, essentially whether this note is off or not
		)
	"""
	notes_tracks = []
	for track in mid_tracks:
		track_notes = []
		# TODO: It will be worth adding more data to the track.
		# For example, the type of instrument that is playing, or a specific tempo.
		for msg in track:
			if msg.type == 'program_change':
				current_instrument = program_to_instrument(msg.program)
			# Only work on messages that describe notes.
			if msg.type == "note_on" or msg.type == "note_off":
				note = (msg.note, msg.velocity, msg.time, msg.velocity > 0, current_instrument)
				track_notes.append(note)
		if len(track_notes) > 0:
			notes_tracks.append(track_notes)
	return notes_tracks


def assign_note (beat: int, ticks_per_beat: int) -> str:
	"""
	Input the time (in ticks) that can be found in midi tracks, and 
	ticks per beat convert time to beats for RTTTL format
	"""
	beat = beat / ticks_per_beat
	if beat == 0:
		return "0"

	elif beat >= 3:
		return "1"

	elif beat >= 1.5:
		return "2"
	
	elif beat >= 0.75:
		return "4"

	elif beat >= 0.375:
		return "8"
	
	elif beat >= 0.1875:
		return "16"
	
	else:
		return "32"


def midi_to_rtttl(midi_tuple_list: list, ticks_per_beat: int) -> str:
	"""
	Input ONE element of the output of extract_midi_tracks function. i.e. just one list should be the input
	It return RTTTL string of the midi note list
	"""

	rtttlList = ""

	for i, tuple in enumerate(midi_tuple_list):
		# skipping the last element, since there's no next tuple's time
		if i == len(midi_tuple_list) - 1:
			break
		
		# note on
		next_tuple = midi_tuple_list[i + 1]
		beat_in_note = assign_note(next_tuple[2], ticks_per_beat)
		if tuple[3] == True:
			newNote = beat_in_note + MIDI2RTTTL.get(tuple[0]) # time of next tuple + note
			rtttlList = rtttlList + "," + newNote
		
		# note off
		else:
			newNote = beat_in_note + "p"
			if beat_in_note != "0":
				rtttlList = rtttlList + "," + newNote
	
	rtttlList = rtttlList[1:]	# removing the first comma
	return rtttlList
