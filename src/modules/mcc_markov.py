# mcc_markov.py
# Code for working with domain-specific Markov models, using 
# Python libraries and our own code.

import numpy as np

"""
TODO: this class needs work. A bit more to the interface to make it friendlier 
for RTTTL format. Some comments can be more specific and code cleanier.

Proof of concept so far.
"""


class MarkovModel:
	def __init__(self, transmat:np.array=None, states:set=None):
		self.states = states
		self.transmat = transmat
		# [tmp] Transition counts used internally and for debugging with repr.
		self._transcounts = {}
		# Define transmat indices for future lookups if model provided.
		self._transmat_idxs = {}
		if not(transmat is None or states is None):
			self._transmat_idxs = dict((s,i) for i,s in enumerate(states))


	def fit(self, event:list):
		"""
		Create a model by fitting a given event (i.e. a ordered list of 
		states). Devise transmat based on state transitions.
		"""
		self.states = set(event)
		self.transmat = np.zeros((len(self.states),len(self.states)))

		# Go through the event and figure out how many 
		# times state s goes to state s' for all s.
		transcounts = {}
		for i in range(len(event)-1):
			if not (event[i], event[i+1]) in transcounts:
				transcounts[(event[i], event[i+1])] = 1
			else:
				transcounts[(event[i], event[i+1])] += 1
		
		# For all states s, populate the transition matrix with 
		# probabilities of s transitioning to itself or any of 
		# the other states.
		for row,s in enumerate(self.states):
			# Record index of the transmat for this state, so 
			# we can reference it later in retrieving state-rows.
			self._transmat_idxs[s] = row
			for col,q in enumerate(self.states):
				if (s,q) in transcounts:
					self.transmat[row][col] = transcounts[(s,q)]

			# Sum row, then divide each element by the sum to get percents.
			rowsum = sum(self.transmat[row])
			for i in range(len(self.transmat[row])):
				self.transmat[row][i] /= rowsum

		# [tmp] Transition counts used internally and for debugging with repr.
		self._transcounts = transcounts


	def predict(self, samples:int, state=None) -> list:
		"""
		Generate a given number of samples from the model. You 
		may pass an initial state to influence the generation.
		"""
		assert not(self.states is None or self.transmat is None), "MCC: cannot predict without model."
		if not state:
			# We have to convert it to a string because apparently numpy 
			# strings are different and can't index dictionaries. Pain.
			state = str(np.random.choice(list(self.states)))

		predictions = []
		for _ in range(samples):
			# Choose one random state from the set of states given the transition probabilities 
			# to other states on the respective row of the transition matrix.
			# We index the first element of whatever the heck np.random.choice returns 
			# because for some reason it is an array.
			state = np.random.choice(list(self.states), 1, p=list(self.transmat[self._transmat_idxs[state]]))[0]
			predictions.append(state)
		
		return predictions
	

	def __repr__(self) -> str:
		return "States:\n" + str(self.states) + \
		"\nTransition matrix:\n" + str(self.transmat) + "\n-------" + \
		"\nTransition counts:\n" + str(self._transcounts)
