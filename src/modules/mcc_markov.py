# mcc_markov.py
# Code for working with domain-specific Markov models, using 
# Python libraries and our own code.

"""
The plan is to split each track in a MIDI file into its own list of notes. 
These notes (i.e. the 4-tuples) will be the states of the Markov chain. 
Have a Markov chain for each track in the song, as tracks with components 
of the melody are more easy to predict than the melody itself.

Workflow idea:
    mcc_parser: extract tracks, their notes, and other info such as tempo
    mcc_markov: model each track with a Markov chain, try to learn to replicate
    mcc_waves: convert sequences of notes and whole tracks into sound waves
    mcc_builder: compile tracks and sound waves, as well as other export tasks
"""