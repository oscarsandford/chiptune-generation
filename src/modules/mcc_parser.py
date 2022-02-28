# mcc_parser.py
# Functions to parse Midi files.

from mido import MidiFile


def open_midi(filepath:str) -> MidiFile:
	assert ".mid" in filepath, "MCC: Cannot open non-MIDI file."
	return MidiFile(filepath, clip=True)


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
            info = (msg.type, msg.tempo, msg.time)
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
			# Only work on messages that describe notes.
			if msg.type == "note_on" or msg.type == "note_off":
				note = (msg.note, msg.velocity, msg.time, msg.velocity > 0)
				track_notes.append(note)
		if len(track_notes) > 0:
			notes_tracks.append(track_notes)
	return notes_tracks
