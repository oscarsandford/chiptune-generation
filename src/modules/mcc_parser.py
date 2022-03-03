# mcc_parser.py
# Functions to parse Midi files.

from mido import MidiFile
from mido import tempo2bpm
import midi_numbers as Instrument


def open_midi(filepath:str) -> MidiFile:
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

	TODO: implement this.
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
				current_instrument = Instrument.program_to_instrument(msg.program)
			# Only work on messages that describe notes.
			if msg.type == "note_on" or msg.type == "note_off":
				note = (msg.note, msg.velocity, msg.time, msg.velocity > 0, current_instrument)
				track_notes.append(note)
		if len(track_notes) > 0:
			notes_tracks.append(track_notes)
	return notes_tracks
