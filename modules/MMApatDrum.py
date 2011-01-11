
# MMApatDrum.py

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
import MMAmidi
from MMApat import PC, seqBump


class Drum(PC):
	""" Pattern class for a drum track. """

	vtype = 'DRUM'
	toneList = [38]

	def setTone(self, ln):
		""" Set a tone list. Only valid for DRUMs.
		    ln[] is not nesc. the right length.
		"""
		
		ln=self.lnExpand(ln, 'Tone')
		tmp = []
		
		for n in ln:
			a=MMAmidi.drumToValue(n)
			if a < 0:
				a=stoi(n, "Expecting a valid drum name or value for "
					"drum, not '%s'" % n)
			if a <0 or a > 127:
				error("Note in Drum Tone list must be 0..127.")
			tmp.append(a)

		self.toneList = seqBump( tmp )

	
	def getPgroup(self, ev):
		""" Get group for a drum pattern.
		
			Tuples: [start, length, volume]
		"""

		a = struct()

		if len(ev) != 3:	
			error("There must be at exactly 3 items in each "
				"group of a drum define, not <%s>." % ' '.join(ev) )
		
		# Volume
					
		a.vol = stoi(ev[2], "Type error in Drum volume.")

		# Duration
		
		a.duration = getNoteLen(ev[1])
		
		a.offset = self.setBarOffset(ev[0])

		return a
		

	
	def trackBar(self, pattern, ctable):
		""" Do a drum bar.
		
		Called from self.bar()
		
		"""
		
		sc = self.seq
		
		for p in pattern:
			tb = self.getChordInPos(p.offset, ctable)
			
			if tb.drumZ:
				continue

			n = self.toneList[sc]
			
			v = self.adjustVolume(p.vol, p.offset)
			if not v:
				continue

			gbl.mtrks[self.channel].addPairToTrack( p.offset,
				self.rTime[sc],
				self.getDur(p.duration), n, v, None )
			

	
