
# MMApatBass.py 

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
	


import MMAglobals;  gbl = MMAglobals
from MMAcommon import *
from MMAharmony import harmonize
from MMApat import PC


class Bass(PC):
	""" Pattern class for a bass track. """

	vtype = 'BASS'	
			
	def getPgroup(self, ev):
		""" Get group for bass pattern.
				
			Tuples:  [start, length, note, volume]
		
		"""
		
		a = struct()
		if len(ev) != 4:	
			error("There must be n groups of 4 in a pattern definition, "
				"not <%s>." % ' '.join(ev) )
		
		n=ev[2][:1]
		if n not in "1234567":
			error("Note offset in Bass must be '1'...'7', "
				"not '%s'" % n )
		a.noteoffset=int(n)-1
		
		a.addoctave = 0
		a.accidental = 0
		
		for n in ev[2][1:]:
			if n == '+':
				a.addoctave += 12
			elif n == '-':
				a.addoctave -= 12
			elif n == '#':
				if a.accidental:
					error("Only 1 accidental permitted in note offset.")
				a.accidental = 1
			elif n == 'b' or n == '&':
				if a.accidental:
					error("Only 1 accidental permitted in note offset.")
				a.accidental = -1
				
			else:
				error("Only '- + # b &' are permitted after a noteoffset. "
					"not '%s'" % n)
		
		a.vol = stoi(ev[3], "Note volume in Bass definition not int.")
		
		a.duration = getNoteLen( ev[1] )

		a.offset = self.setBarOffset(ev[0])
					

		return a


	def trackBar(self, pattern, ctable):
		""" Do the bass bar.
		
		Called from self.bar()
		
		"""
		
		sc = self.seq
		unify = self.unify[sc]

		for p in pattern:
			ct = self.getChordInPos(p.offset, ctable)

			if ct.bassZ:
				continue
						

			note = ct.chord.scaleList[p.noteoffset] + p.addoctave + p.accidental

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
						n, 	v, unify )
						
			if self.harmony[sc]:
				h = harmonize(self.harmony[sc], note, ct.chord.noteList)
				for n in h:
					gbl.mtrks[self.channel].addPairToTrack(
						p.offset,
						self.rTime[sc],
						self.getDur(p.duration),
						self.adjustNote(n), 
						self.adjustVolume(p.vol, -1),
						unify )
						

	

