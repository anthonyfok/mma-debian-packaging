
# MMAharmony.py

"""
	This module is an integeral part of the program 
	MMA - Musical Midi Accompaniment.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

	Bob van der Poel <bvdp@uniserve.com>
	
"""
	




from MMAcommon import *

def harmonize(tp, note, chord):
	""" Get harmony note(s) for given chord. """
	
	if tp == '2':
		return [ gethnote(note, chord) ]
		
	elif tp == '2ABOVE':
		return [ gethnote(note, chord)+12 ]

	elif tp == '3':
		a = gethnote(note, chord)
		b = gethnote(a, chord)
		return [a, b]
	
	elif tp == '3ABOVE':
		a = gethnote(note, chord)
		b = gethnote(a, chord)
		return [a+12, b+12]

	elif tp == 'OPEN':
		a = gethnote(note, chord)
		return [ gethnote(a, chord) ]

	elif tp == 'OPENABOVE':
		a = gethnote(note, chord)
		return [ gethnote(a, chord)+12 ]

	elif tp in ('8', '8BELOW'):
		return [ note - 12]
		
	elif tp == '8ABOVE':
		return [ note + 12 ]
		
	elif tp in ('16', '16BELOW'):
		return [ note - 24]
		
	elif tp == '16ABOVE':
		return [ note + 24 ]

	elif tp == '8BOTH':
		return [ note - 12, note + 12 ]
		
	elif tp == '16BOTH':
		return [ note + 24 , note - 24 ]

	else:
		error("Unknown harmony type '%s'." % tp)


def gethnote(note, chord):
	""" Determine harmony notes for a note based on the chord.
	
			note - midi value of the note
		
			chord - list of midi values for the chord
		
		
		This routine works by creating a chord list with all
		its notes having a value less than the note (remember, this
		is all MIDI values). We then grab notes from the end of
		the chord until one is found which is less than the original
		note.
	
	"""
	
	wm="No harmony note found since no chord, using note " + \
		"0 which will sound bad."
			

	if not chord:		# should never happen!
		warning(wm)			
		return 0
		
	ch = list(chord)	# copy chord and sort
	ch.sort()
	
	# ensure that the note is in the chord
	
	while ch[-1] < note:
		for i,n in enumerate(ch):
			ch[i]+=12
			
	while ch[0] >= note:
		for i,v in enumerate(ch):
			ch[i]-=12

	# get one lower than the note
	
	while 1:
		if not ch:			# this probably can't happen
			warning(wm)
			return 0
			
		h=ch.pop()
		if h<note: break
	
	return h	
	
	
