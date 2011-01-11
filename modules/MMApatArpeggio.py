
# MMApatArpeggio.py

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
import MMAglobals;  gbl = MMAglobals
from MMAcommon import *
from MMAharmony import harmonize
from MMApat import PC


class Arpeggio(PC):
	""" Pattern class for an arpeggio track. """

	vtype = 'ARPEGGIO'
	arpOffset=-1
	arpDirection=1
	ourChord = []
		
	def getPgroup(self, ev):
		""" Get group for apreggio pattern.
		
			Tuples: [start, length, volume]
		"""
	
		a = struct()
		if len(ev) != 3:	
			error("There must be exactly 3 items in each group "
				"for apreggio define, not <%s>." % ' '.join(ev) )

		a.vol = stoi(ev[2], "Type error in Arpeggio definition.")
		
		a.duration = getNoteLen(ev[1])
				
		a.offset = self.setBarOffset(ev[0])
		
		return a
	 		

	
	def trackBar(self, pattern, ctable):
		""" Do a arpeggio bar.
		
		Called from self.bar()
		
		"""
		
		sc = self.seq
		direct = self.direction[sc]
		
		for p in pattern:
			tb = self.getChordInPos(p.offset, ctable)

			if tb.arpeggioZ:
				continue

			if direct == 'DOWN':
				self.arpDirection = -1

			if self.chordLimit:
				tb.chord.limit(self.chordLimit)

			if self.compress[sc]:
				tb.chord.compress()
	
			if self.invert[sc]:
				tb.chord.invert(self.invert[sc])
			
			ourChord = tb.chord.noteList[:]
			
			t=[ x*12 for x in range(1, self.chordRange[sc])]
			for a in t:
				ourChord += [ x+a for x in tb.chord.noteList]

				
			if direct == 'BOTH':
				if self.arpOffset < 0:	
					self.arpOffset = 1
					self.arpDirection = 1
				elif self.arpOffset >= len(ourChord):
					self.arpOffset = len(ourChord)-2
					self.arpDirection = -1

			elif direct == 'UP':
				if self.arpOffset >= len(ourChord) or self.arpOffset < 0:
					self.arpOffset = 0
					self.arpDirection = 1
					
			elif direct == 'DOWN':
				if self.arpOffset < 0 or self.arpOffset >= len(ourChord):
					self.arpOffset = len(ourChord)-1
					self.arpDirection = -1

			if direct == 'RANDOM':
				note  = random.choice(ourChord)
			else:
				note = ourChord[self.arpOffset]

			self.arpOffset += self.arpDirection
		
			v=self.adjustVolume(p.vol, p.offset)
			if not v:
				continue

			unify = self.unify[sc]
			
			if not self.harmonyOnly[sc]:
				gbl.mtrks[self.channel].addPairToTrack(
					p.offset,
					self.rTime[sc],
					self.getDur(p.duration),
					self.adjustNote(note),
					v,
					unify )

			if self.duplicate[sc]:
				n = self.adjustNote(note) + self.duplicate[sc]
				if n>=0 and n<128:
					gbl.mtrks[self.channel].addPairToTrack(
						p.offset,
						self.rTime[sc],
						self.getDur(p.duration),
						n, 	v, unify )

			if self.harmony[sc]:
				h = harmonize(self.harmony[sc], note, ourChord)
				for n in h:
					gbl.mtrks[self.channel].addPairToTrack(p.offset,
						self.rTime[sc],
						self.getDur(p.duration),
						self.adjustNote(n), 
						self.adjustVolume(p.vol, -1),
						unify )
			
			tb.chord.reset()	# important, other tracks chord object


