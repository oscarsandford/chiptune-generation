import numpy as np


def _midi_to_freq(pitch):
    return 440*(2**((pitch-69)/12.0))

# Based on the equation for approximating a triangle wave with harmonics.
# https://en.wikipedia.org/wiki/Triangle_wave#Harmonics
def generate_triangle(pitch, nharmonics, dur=1.0, amp=1.0, sr=44100):    
    f0 = _midi_to_freq(pitch)
    t = np.arange(0, dur, 1.0/sr)
    x = np.zeros(t.shape[0])
    for i in range(nharmonics):
        n = 2*i + 1
        x += ((-1)**i)*(n**(-2))*(np.sin(2*np.pi*f0*n*t))
    return (8/(np.pi**2)) * x

# props: list 
# | idx 0 : proportion of time for attack stage
# | idx 1 : proportion of time for decay stage
# | idx 2 : proportion of time for sustain stage
# |> proportion of time for release is the remaining duration
def adsr_envelope(duration: float, props: list, sr:int=44100) -> np.array:
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
