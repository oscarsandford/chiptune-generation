# mcc_markov.py
# Code for working with general-purpose Markov models.
# Written from scratch, only using numpy.
# - SimpleMarkov is a more naive, first-order implementation.
# - KMarkov can model higher-order processes and make predictions 
# 	adaptively using a reduction algorithm.
# 

import numpy as np


class SimpleMarkov:
	def __init__(self, states:set=None, transmat=None, epsilon:float=0.0):
		"""
		A class for constructing first-order Markov models.
				
		The first two optional arguments on initialization allow for immediate model construction 
		given a set of states with length N and a NxN transition matrix array.
		
		>>> mm = SimpleMarkov(states=["S", "C"], transmat=np.array([[0.7, 0.3],[0.2, 0.8]]))

		However, the model can be initialized without these and manually 
		trained by examples using the fit() method.
		
		>>> mm = SimpleMarkov()
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
		assert not(self.states is None or self.transmat is None), "MCC: Cannot predict without model."
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
	def __init__(self, k:int):
		"""
		A class for fitting and sampling k-order Markov models where k is the 
		number of previous states that the next state is dependent on. For example, 
		if k=1, we only consider the previous state when predicting the next state. 

		If k=5, learning the model becomes more complicated than simply mapping 
		a single state to a set of possible next states and their associated 
		probabilities. 
		
		The set of previous states (of size k) are called priors. The transition probabilities 
		(TP) table creates keys out of these priors, and under these priors we store another 
		table that maps the possible next states (given the priors) to their associated 
		probabilities. This makes TP prior and then next state probability lookups efficient 
		and flexibility as opposed to a multi-dimensional array structure. 
		
		More details on the fitment and prediction algorithms can be found in the descriptions 
		of their associated methods.
		
		----

		Note that the model itself cannot be constructed in initialization. 
		That is, you cannot pass in a TP table and define your own states on construction.

		Use fit() to build the model for k-order processes. We can fit() an event to 
		a KMarkov object if the size of the event is greater than k. 
		Use predict() to generate a given number of samples, once the model is fitted. 

		The following example shows how this class works to generate musical notes in RTTTL format:

		>>> mm = KMarkov(3)
		>>> mm.fit("16e6,16e6,32p,8e6,16c6,8e6,8g6,8p,8g,8p,8c6")
		>>> mm.predict(15)
		['8p', '16g6', '16f#6', '16f6', '16d#6', '16p', '16e6', '16p', '16g#', 
		'16a', '16c6', '16p', '16a', '16c6', '16d6', '8p', '16g6', '16f#6']
		
		Note that issues with predict() can occur when the order k of the model is too 
		high, the number of examples fit()'d is too small, and the number of samples 
		passed to predict() is too high. 

		A good heuristic is to provide as much data to fit() as possible. For this reason, SimpleMarkov 
		is current a safer model to use, but is far less configurable and also less accurate.
		"""
		self.k = k
		# Transition probabilities are stored in a dictionary for more efficient and flexible storage.
		# The format is: 
		# TP[`string of prior states`] = 
		# 	{`next state` : `probability to do this transition to next state`}
		self.TP = {}


	def fit(self, event:list or str):
		"""
		Do fitment. You can pass a command-separated string of states, like in RTTTL format, or as a list. 

		Walk through the event, creating keys for TP with k consecutive states ("priors") followed by its 
		subsequent state ("next"). After combing through the event, return to the lookup table of priors 
		and replace the occurrence counts with probabilities.

		The fit() method is linear in the order of `len(event) - k`.
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


	def predict(self, samples:int, priors:str=None, DEBUG_LVL:int=0) -> str:
		"""
		Generate a given number of samples from the model. Returns a comma-separated string of states.
		OPTIONAL: provide a sequence of priors as a comma-separated string. Prediction will start 
		from the last k states in the priors. Use this to extend the track trained on by just passing 
		the string you used as a training event to the priors parameter.

		The set of predictions is initialized through a random choice of priors. 
		One could allow passing a set of states to initialize predictions on. (TODO)
		
		In order to predict a single next state, make it so that the set of priors (or a reducible suffix) can 
		be found in the TP lookup. 
		
		If yes, great. Probabilistically choose one of the prior's possible next states.
		
		If not, reduce the priors by removing one prior state from the front. Check again, but instead of 
		checking for an exact match, check if the reduced priors are a suffix of another key. If we find 
		one such inexact match, set the priors to the full priors that were matched by the reduced priors. 
		They will be returned on the next run of the loop.
		
		If reduction goes to the last prior, randomly chose a sequence of priors that end in the remaining state. 
		"""
		assert not self.states is None, "MCC: Cannot predict without model. Remember to fit() first."

		if priors is None:
			# Grab a random set of k consecutive states that will definitely have a next state.
			preds = str(np.random.choice(list(self.TP.keys()))).split(",")
		else:
			assert "," in priors, "MCC: Separate priors in string representation with commas."
			preds = priors.split(",")[-self.k:]

		for i in range(samples):
			# Only consider the k most recent states visited.
			priors = ",".join(preds[-self.k:])
			if DEBUG_LVL > 0:
				print(i, " init priors:", priors)

			while not priors in self.TP:
				priors_list = priors.split(",")
				
				# Reduce from beginning.
				if len(priors_list[1:]) > 0:
					priors = ",".join(priors_list[1:])
					for ps in self.TP:
						if ps[-len(priors):] == priors:
							priors = ps[-len(priors):]
							break
				
				# No more states left to reduce? Then take that last state 
				# and randomly choose a set of priors that ends in that state
				# of all the priors that end in this state. 
				else:
					last_state = ",".join(priors_list)
					possible_priors = [k for k in self.TP if k[-len(last_state):] == last_state]
					priors = str(np.random.choice(possible_priors))

				if DEBUG_LVL > 0:
					print("  reduced priors:", priors)

			if DEBUG_LVL > 1:
				print(" end priors:", priors)
				print(" keys: ", list(self.TP[priors].keys()))
				print(" vals: ", list(self.TP[priors].values()))

			# Now TP is safe to access. Probabilistically decided which next state to return.
			next = str(np.random.choice(list(self.TP[priors].keys()), p=list(self.TP[priors].values())))

			if DEBUG_LVL > 0:
				print(" next:", next)
				print("-"*20)

			preds.append(next)
		
		return ",".join(preds)
