import numpy as np
import matplotlib.pyplot as plt
import mcc_waves

# Break a list of tracks containing mido messages 
# into a list of tracks containing notes.
def parse_tracks(raw: list) -> list:
    tracks = []
    for i, track in enumerate(raw):
        track_notes = []
        for msg in track:
            if msg.type == "note_on" or msg.type == "note_off":
                note = (msg.note, msg.velocity, msg.time, msg.velocity > 0)
                track_notes.append(note)
        if len(track_notes) > 0:
            tracks.append(track_notes)
    return tracks

# Add a wave to a list of waves at index idx. Extend 
# the waves list to accommodate this as needed.
def _add_wave(waves: list, wave: list, idx: int):
    if len(waves) < len(wave):
        waves += [0.]*(len(wave)-len(waves))
    waves[idx:len(wave)] = wave

# Build triangle waves for each note. enveloping them with ADSR as needed.
# Returns a list of lists: for each track, the triangle notes for each track.
def build_track_waves(tracks: list, tri_harm:int=4, tri_rate:int=1000, do_envl:bool=False) -> list:
    track_waves = []
    for track in tracks:
        waves = []
        ptr = 0
        for i, note in enumerate(track):
            if note[3]:
                for n in track[i:]:
                    if n[0] == note[0] and not n[3]:
                        ntime = n[2]
                        break
            else:
                ntime = 0
                
            note_wave = mcc_waves.generate_triangle(note[0], tri_harm, ntime/tri_rate)
            if do_envl:
                envl = mcc_waves.adsr_envelope(ntime/tri_rate, [0.1, 0.2, 0.5])
                note_wave = note_wave[:-1] * envl
            
            _add_wave(waves, note_wave, ptr)
            ptr += len(note_wave)
        
        track_waves.append(waves)
    return track_waves

# Returns the shortest length list element in a list of lists.
# Used for truncating tracks longer than the minimum length track.
def _min_len_nonzero(lili: list) -> int:
    minlen = np.inf
    for li in lili:
        if len(li) < minlen:
            minlen = len(li)
    return minlen

# Given a list of tracks an an option to truncate them, 
# returns a list of each list added element-wise.
def combine_tracks(tracks: list, truncate:bool=True) -> list:
    assert len(tracks) > 0, "Tracks must be non-empty."
    if truncate:
        l = _min_len_nonzero(tracks)
        tracks = [t[:l] for t in tracks]
    
    combined = np.zeros(len(tracks[0]))
    for t in tracks:
        combined += t
    return combined

# Driver code helper. Calls the above functions with given data 
# and plots the resulting signals.
def create_melody(data: list, title: str, envelope:bool=False):
    tracks = parse_tracks(data)
    twaves = build_track_waves(tracks, tri_rate=650, do_envl=envelope)
    result = combine_tracks(twaves)
    plt.plot(result)
    plt.title(title)
    return result
