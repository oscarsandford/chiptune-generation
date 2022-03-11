# mcc_markov.py
# Code for working with domain-specific Markov models, using 
# Python libraries and our own code.

import numpy as np

"""
TODO: 

Clean up KMarkov, and MarkovModel in terms of code and documentation.

KMarkov is still rudimentary, but seems to outclass MarkovModel off the bat.
However, it is much slower. Keep both around just in case.
"""

class MarkovModel:
	def __init__(self, states:set=None, transmat=None, epsilon:float=0.0):
		"""
		A class for constructing first-order Markov models.
				
		The first two optional arguments on initialization allow for immediate model construction 
		given a set of states with length N and a NxN transition matrix array.
		
		>>> mm = MarkovModel(states=["S", "C"], transmat=np.array([[0.7, 0.3],[0.2, 0.8]]))

		However, the model can be initialized without these and manually 
		trained by examples using the fit() method.
		
		>>> mm = MarkovModel()
		>>> mm.fit(["S", "S", "C", "S", "C"])
		
		It is important to note that the states can be any hashable type that can be put 
		into a set, not just strings.

		The `epsilon` parameter can be set on the range [0.0, 1.0] in order to bias a greedy 
		decision making choice in prediction. 
			If epsilon=1.0, the most probable transition will always be chosen. Careful, as this 
				can lead to self-loops.
			If epsilon=0.0 (by default), the transition probabilities will be weighted accordingly. 
			If epsilon=0.5, there will be a 50% chance of taking the most probable action, and a 
				50% chance of making a weighted choice between the other actions.
		
		This was a terrible idea. Only mess with epsilon if you're feeling chaotic.
		"""
		self.states = states
		self.transmat = transmat
		self.epsilon = epsilon

		if not(transmat is None or states is None):
			assert len(transmat.shape) == 2 and transmat.shape[0] == transmat.shape[1], "MCC: transmat of inadequate shape."
			assert len(states) == transmat.shape[0], "MCC: transmat row dimension does not match state set cardinality."
			# Assure that the set of states is a set of unique elements in the case a list is passed by accident.
			self.states = list(set(states))
			# Define transmat indices for future state-index lookups if model provided.
			self._transmat_idxs = dict((s,i) for i,s in enumerate(states))
		else:
			# Otherwise, we will construct this during training.
			self._transmat_idxs = {}

		assert 0 <= epsilon <= 1.0, "MCC: epsilon must be in range [0.0, 1.0]."


	def fit(self, event: list or str):
		"""
		Create a model by fitting a given event as either:
			an ordered list of states OR 
			a string of states separated by commas. 
		Devise transmat based on state transitions.
		"""
		if type(event) is str:
			assert "," in event, "MCC: Separate states in string representation with commas."
			self.states = self.event.split(",")
		else:
			self.states = list(set(event))
		
		self.transmat = np.zeros((len(self.states),len(self.states)))

		# Go through the event and figure out how many 
		# times state s goes to state s' for all s.
		transcounts = {}
		for i in range(1, len(event)):
			if not (event[i-1], event[i]) in transcounts:
				transcounts[(event[i-1], event[i])] = 1
			else:
				transcounts[(event[i-1], event[i])] += 1
		
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
		else:
			assert state in self.states, "MCC: Invalid provided state."

		predictions = []
		for _ in range(samples):
			if np.random.random() < self.epsilon:
				# With epsilon chance, we choose the most probable next state.
				# If epsilon=0.0, as by default, this never happens.
				state = list(self.states)[np.argmax(self.transmat[self._transmat_idxs[state]])]
			else:
				# Choose one state from the set of states given the transition probabilities 
				# to other states on the respective row of the transition matrix.
				# We index the first element of whatever the heck np.random.choice returns 
				# because for some reason it is an array.
				state = np.random.choice(list(self.states), 1, p=self.transmat[self._transmat_idxs[state]])[0]
			predictions.append(state)
		
		return predictions
	

	def __repr__(self) -> str:
		return "States:\n" + str(self.states) + \
		"\nTransition matrix:\n" + str(self.transmat)




class KMarkov():
	def __init__(self, order:int, states:set=None):
		"""
		The `order` parameter is set to increase the number of previous states that are 
		considered when predicting the next state. This will make the transition matrix more 
		complex as a result. Use fit() to build the model for higher-order processes.
		"""
		self.k = order
		# Transition probabilities are stored in a dictionary for more efficient and flexible storage.
		# The format is 
		# TP[string of prior states] = (next state, probability to do this transition to next state)
		self.TP = {}
		if not states is None:
			self.states = list(set(states))


	def fit(self, event:list or str):
		"""
		Do fitment.

		TODO: this docstring needs more work. Elaborate on the workings.
		"""
		if type(event) is str:
			assert "," in event, "MCC: Separate states in string representation with commas."
			event = event.split(",")
		
		assert len(event) > self.k, f"MCC: Cannot fit with order {self.k} to event of size {len(event)}."
		self.states = list(set(event))

		# Create counts of how many times a sequence of o states results in a new state s.
		for i in range(len(event)-self.k):

			priors = ",".join(event[i:i+self.k])
			next = event[i+self.k]

			# Case 1: prior states already recorded and next state is indexable and incrementable.
			if priors in self.TP and next in self.TP[priors]:
				self.TP[priors][next] += 1.0

			# Case 2: prior states already recorded BUT next state is not yet included as possible outcome.
			elif priors in self.TP:
				self.TP[priors][next] = 1.0

			# Case 3: prior states not recorded. Initialize them with next state as only possible outcome (so far).
			else:
				self.TP[priors] = {next: 1.0}

		# Replace counts with probabilities of that selection 
		# of prior states switching to the next state.
		for priors in self.TP:
			csum = sum(self.TP[priors].values())
			for next in self.TP[priors]:
				self.TP[priors][next] /= csum

		# for p in self.TP:
		# 	print(p ,"-->" , self.TP[p])


	def predict(self, samples:int, init_states=None) -> list:
		"""
		Generate a given number of samples from the model.

		TODO: this docstring needs work. Elaborate on the why and how.
		"""
		assert not(self.states is None or self.TP is None), "MCC: cannot predict without model."

		# Grab a random set of k consecutive states that will definitely have a next state.
		preds = str(np.random.choice(list(self.TP.keys()))).split(",")

		for i in range(samples):

			# Predict the next state given the current predictions.
			# If we find at least one exact match, we choose the next state 
			# probabilistically, depending on the probability distribution 
			# among the possible next states.
			# If we don't find an exact match, look for the next shortest 
			# match, starting by reducing the size from the start.
			# i.e.
			# predictions[-o:] = [c,d] (last o elements we predict with)
			# ----
			# don't match at all: e.g. [a,c,d,b], [c,d,a], ...
			# ----
			# prev:[a,b,c,d] -> next:[e]
			# reduce
			# prev:[b,c,d] -> next:[e]
			# reduce again
			# prev:[c,d] -> next:[e]
			# => next state is [e]

			# Only consider the k most recent states visited.
			priors = ",".join(preds[-self.k:])
			# print(i, " init priors:", priors)

			while not priors in self.TP:
				priors_list = priors.split(",")
				
				# Reduce from beginning.
				if len(priors_list[1:]) > 0:
					priors = ",".join(priors_list[1:])
				
				# No more priors? Then take the last 
				# state and find the first (TODO: or random?)
				# set of priors in the transition probability 
				# lookup and set those as the priors.
				else:
					priors = ",".join(priors_list)
					for k in self.TP:
						if k[-len(priors):] == priors:
							priors = k
							break

				# print("  reduced priors:", priors)

			# print("end priors:", priors)
			# Now TP is safe to access. Probabilistically decided which next 
			# state to return.
			# print(" keys: ", list(self.TP[priors].keys()))
			# print(" vals: ", list(self.TP[priors].values()))

			next = str(np.random.choice(list(self.TP[priors].keys()), p=list(self.TP[priors].values())))
			# print(" next:", next)
			# print("-"*20)

			preds.append(next)
		
		return preds
