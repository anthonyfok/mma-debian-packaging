
# MMApatScale.py

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


class Scale(PC):
	""" Pattern class for a Scale track. """

	vtype = 'SCALE'
	
	lastNote = -1
	lastChord = None
	lastStype = None
	lastDirect = 1
	lastRange = 0
	sOffset = 0
	notes = None
	dirfact = 1

	def getPgroup(self, ev):
		""" Get group for scale patterns.
		
			Tuples: [start, length, volume]
		"""

		a = struct()
		if len(ev) != 3:	
			error("There must be at exactly 3 items in each group " 
				"in a Scale definition, not <%s>." % ' '.join(ev))
			
		a.vol = stoi(ev[2],"Type error in Scale definition")

		a.duration = getNoteLen(ev[1])				
					
		a.offset = self.setBarOffset(ev[0])	
					
		return a
	

	def trackBar(self, pattern, ctable):
		""" Do a scale bar.
		
			Called from self.bar()
		"""
	
		sc = self.seq
		direct = self.direction[sc]
		unify = self.unify[sc]
		
		# If the range or direction has changed, we just start
		# with a new scale. 


		t = self.chordRange[sc]
		if t != self.lastRange:
			self.lastRange = t
			self.lastChord = None
			
		if self.lastDirect != direct:
			self.lastDirect = direct
			self.lastChord = None

		for p in pattern:
		
			tb = self.getChordInPos(p.offset, ctable)
			
			if tb.scaleZ:
				continue


			thisChord = tb.chord.tonic + tb.chord.chordType
			stype = self.scaleType[sc]
			
			if thisChord != self.lastChord or stype != self.lastStype:
				self.lastChord = thisChord
				self.lastStype = stype
				
				if stype == 'CHROMATIC':
					self.notes = [ tb.chord.rootNote + x for x in range(0,12)]
					
				else:
					self.notes = list(tb.chord.scaleList)

				""" Get the current scale and append enuf copies
					together for RANGE setting. If Range happens
					to be 0 or 1 we end up with a single copy.
				"""
				
				l=self.chordRange[sc]	# RANGE 1...x (def. == 1)
				
				o=12
				while(l>1):
					for a in tb.chord.scaleList:
						self.notes.append(a+o)
					o+=12
					l-=1		
				
				if self.lastNote > -1:
					if self.notes.count(self.lastNote):
						self.sOffset = self.notes.index(self.lastNote)
						
					else:
						self.sOffset=len(self.notes)-1
						for  i, a in enumerate(self.notes):
							if a>self.lastNote:
								self.sOffset = i
								break
				
				else:
					self.sOffset = 0
								
			
			# Keep offset into note list in range
			
			if self.sOffset >= len(self.notes):
				if direct == 'BOTH':
					self.dirfact = -1
					self.sOffset = len(self.notes)-2
				else:
					self.sOffset = 0
					
			elif self.sOffset < 0:
				if direct == 'BOTH':
					self.dirfact = 1
					self.sOffset = 1
				else:
					self.sOffset = len(self.notes)-1
					
			if direct == 'RANDOM':
				note = random.choice(self.notes)
			else:
				note = self.notes[self.sOffset] 
				self.sOffset += self.dirfact
			
			self.lastNote = note
			
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
						n,	v, unify )

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


