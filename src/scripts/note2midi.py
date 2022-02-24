# Hacky script to generate a table for note names to numerical MIDI notes.

d = dict()
octv = 0
li = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
for i in range(24,108):
	if (i-24)%12 == 0:
		octv += 1
	ext = str(octv) if octv in [4,5,6,7] else ""
	d[li[(i-24)%12] + str(octv)] = i

print(d)
print(len(d))
