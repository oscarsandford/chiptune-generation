# mcc_markov.py
# Code for working with domain-specific Markov models, using 
# Python libraries and our own code.

import numpy as np


class MarkovModel:
	def __init__(self, states:set=None, transmat=None):
		"""
		A class for constructing first-order Markov models.
		
		Optional arguments on initialization allow for immediate model construction given 
		a set of states with length N and a NxN transition matrix array.
		
		>>> mm = MarkovModel(states=["S", "C"], transmat=np.array([[0.7, 0.3],[0.2, 0.8]]))

		However, the model can be initialized without these and manually 
		trained by example using the fit() method.
		
		>>> mm = MarkovModel()
		>>> mm.fit(["S", "S", "C", "S", "C"])
		
		It is important to note that the states can be any hashable type that can be put 
		into a set, not just strings.
		"""
		self.states = states
		self.transmat = transmat

		if not(transmat is None or states is None):
			assert len(transmat.shape) == 2 and transmat.shape[0] == transmat.shape[1], "MCC: Transmat of inadequate shape."
			assert len(states) == transmat.shape[0], "MCC: Transmat row dimension does not match state set cardinality."
			# Assure that the set of states is a set of unique elements in the case a list is passed by accident.
			self.states = set(states)
			# Define transmat indices for future state-index lookups if model provided.
			self._transmat_idxs = dict((s,i) for i,s in enumerate(states))
		else:
			# Otherwise, we will construct this during training.
			self._transmat_idxs = {}


	def fit(self, event:list):
		"""
		Create a model by fitting a given event as a ordered list 
		of states. Devise transmat based on state transitions.
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

			# Sum row, then divide each element by the sum to get probabilities.
			rowsum = sum(self.transmat[row])
			for i in range(len(self.transmat[row])):
				self.transmat[row][i] /= rowsum


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
			state = np.random.choice(list(self.states), 1, p=self.transmat[self._transmat_idxs[state]])[0]
			predictions.append(state)
		
		return predictions
	

	def __repr__(self) -> str:
		return "States:\n" + str(self.states) + \
		"\nTransition matrix:\n" + str(self.transmat)
