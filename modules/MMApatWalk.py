
# MMApatWalk.py

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
	



import random
from MMAharmony import harmonize
import MMAglobals;  gbl = MMAglobals
from MMAcommon import *
from MMApat import PC


class Walk(PC):
	""" Pattern class for a walking bass track. """

	vtype = 'WALK'
	
	def getPgroup(self, ev):
		""" Get group for walking bass pattern.
		
			Tuples: [start, length, volume]
		"""

		a = struct()
		if len(ev) != 3:	
			error("There must be at exactly 3 items in each group in " 
					"a Walking Bass definition, not <%s>." % ' '.join(ev))
			
		a.vol = stoi(ev[2], "Type error in Walking Bass definition")

		a.duration = getNoteLen(ev[1])				
					
		a.offset = self.setBarOffset(ev[0])	
					
		return a
		

	walkChoice = 0	
	
	def trackBar(self, pattern, ctable):
		""" Do a waling  bass bar.
		
		Called from self.bar()
		
		"""

		sc=self.seq		
		dir = self.direction[sc]
		unify = self.unify[sc]
		
		for p in pattern:
		
			tb = self.getChordInPos(p.offset, ctable)
			
			if tb.walkZ:
				continue
				
			root = tb.chord.rootNote 		# root note of chord

			""" Create a note list from the current scale. We do
				this for each beat, but it's pretty fast. The note
				list is simply notes 0..6 of the scale PLUS notes
				1..5 reversed. So, a Cmajor chord would result in
				the note list (0,2,4,5,7,9,7,5,4,2).
				
				Note that we deliberately skip the 7th. Too often
				the chord is a Major but the melody note will be
				the dom. 7th and the M7 will sound off. So, just
				err on the side of caution.
				
				If DIR is UP or DOWN we don't append the 2nd half
				of the scale.
				
				If DIR is DOWN we reverse the order as well.
			"""
			
			wNotes = list(tb.chord.scaleList[0:6])
			if dir not in ('UP', 'DOWN'):
				b = list(tb.chord.scaleList[1:5])
				b.reverse()
				wNotes += b

			if dir == 'DOWN':
				wNotes.reverse()				
		

			# Ensure that the offset is in range.
			
			if self.walkChoice >= len(wNotes) or self.walkChoice < 0:
				self.walkChoice = 0

			note = wNotes[self.walkChoice] 

			""" Adjust offset for next time. If the direction is
				up/down we just increment the pointer. If we have
				direction set to RANDOM then we select either -1,
				0 or 1 with equal change for moving up, down or
				not-at-all. With BOTH we have a preference to move up.
			"""		
		
			
			if dir in ('UP', 'DOWN'):
				self.walkChoice += 1
			elif dir == 'RANDOM':
				self.walkChoice += random.choice((0,1,-1))
			else:	# BOTH			
				self.walkChoice += random.choice( (-1,0,0,2,2,1,1,1,1,1,1,1))

	
			v=self.adjustVolume(p.vol, p.offset)

			if not v:
				continue

			if not self.harmonyOnly[sc]:
				gbl.mtrks[self.channel].addPairToTrack(
					p.offset,
					self.rTime[sc],
					self.getDur(p.duration),
					self.adjustNote(note),
					v, unify )
	
			if self.duplicate[sc]:
				n = self.adjustNote(note) + self.duplicate[sc]
				if n>=0 and n<128:
					gbl.mtrks[self.channel].addPairToTrack(
						p.offset,
						self.rTime[sc],
						self.getDur(p.duration),
						n,	v, unify)

			if self.harmony[sc]:
				ch = self.getChordInPos(p.offset, ctable).chord.noteList
				h = harmonize(self.harmony[sc], note, ch)
				for n in h:
					gbl.mtrks[self.channel].addPairToTrack(
						p.offset,
						self.rTime[sc],
						self.getDur(p.duration),
						self.adjustNote(n), 
						self.adjustVolume(p.vol, -1),
						unify )



