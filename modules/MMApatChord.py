
# MMApatChord.py

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
from MMApat import PC


class Chord(PC):
	""" Pattern class for a chord track. """

	vtype = 'CHORD'
	
	
	def getPgroup(self, ev):
		""" Get group for chord pattern.
		
			Tuples: [start, length, volume (,volume ...) ]
		"""
			
		a = struct()
		if len(ev) < 3:	
			error("There must be at least 3 items in each group "
				"of a chord pattern definition, not <%s>." % ' '.join(ev))
		
		a.vol = []
		for i in ev[2:]:
			a.vol.append(stoi(i,
				"Expecting integer in vols for Chord definition."))

		while(len(a.vol)<8):	# force 8 volumes
			a.vol.append(a.vol[-1])
		
		a.duration = getNoteLen(ev[1])	
							
		a.offset = self.setBarOffset(ev[0])
			
		return a
		

	def chordVoicing(self, chord, vMove):
		""" Voicing algorithm by Alain Brenzikofer. """
		

		sc = self.seq
		vmode=self.voicing.mode

		if vmode == "OPTIMAL":

			# Initialize with a voicing around centerNote

			chord.center1(self.lastChord)

			# Adjust range and center

			if not (self.voicing.bcount or self.voicing.random):
				chord.center2(self.voicing.center, self.voicing.range/2)


			# Move voicing

			elif self.lastChord:
				if (self.lastChord != chord.noteList ) and vMove:
					chord.center2(self.voicing.center,self.voicing.range/2)
					vMove = 0
					
					# Update voicingCenter
					
					sum=0
					for n in chord.noteList:
						sum += n
					c=sum/chord.noteListLen
					
					"""	If using random voicing move it it's possible to
						get way off the selected octave. This check ensures
						that the centerpoint stays in a tight range.
						Note that if using voicingMove manually (not random)
						it is quite possible to move the chord centers to very
						low or high keyboard positions!
					"""

					if self.voicing.random:
						if   c < -4: c=0
						elif c >4: c=4
					self.voicing.center=c

		elif vmode == "COMPRESSED":
			chord.compress()
		
		elif vmode == "INVERT":
			if chord.rootNote < -2:
				chord.invert(1)

			elif chord.rootNote > 2:
				chord.invert(-1)
			chord.compress()
				
		self.lastChord = chord.noteList[:]
		
		return vMove
		

	def trackBar(self, pattern, ctable):
		""" Do a chord bar. Called from self.bar() """
			
		sc = self.seq
		unify = self.unify[sc]
		
		"""	Set voicing move ONCE at the top of each bar.
			The voicing code resets vmove to 0 the first
			time it's used. That way only one movement is
			done in a bar.
		"""
		
		vmove = 0
		
		if self.voicing.random:
			if random.randrange(100) <= self.voicing.random:
				vmove = random.choice((-1,1))
		elif self.voicing.bcount and self.voicing.dir:
			vmove = self.voicing.dir


		for p in pattern:
			tb = self.getChordInPos(p.offset, ctable)

			if tb.chordZ:
				continue

			self.crDupRoot = self.dupRoot[sc]
			
			vmode = self.voicing.mode
			vols = p.vol[0:tb.chord.noteListLen]
			
			""" Limit the chord notes. This works even if
				THERE IS A VOICINGMODE!
			"""
			
			if self.chordLimit:
				tb.chord.limit(self.chordLimit)
				
			""" Compress chord into single octave if 'compress' is set
				We do it here, before octave, transpose and invert!
				Ignored if we have a VOICINGMODE.
			"""
			
			if self.compress[sc] and not vmode:
				tb.chord.compress()

			# Do the voicing stuff.
			
			if vmode:
				vmove=self.chordVoicing(tb.chord, vmove)

			# Invert. 

			if self.invert[sc]:
				tb.chord.invert(self.invert[sc])

			""" Duplicate the root. This can be set from a DupRoot command
				or by chordVoicing(). Notes:
				-> Root was set earlier and is guaranteed to be the root
					note of the current chord.
				-> The volume for the added root will be loudest of the
					notes in the chord.
				-> If the new note (after transpose and octave adjustments
					is out of MIDI range it will be ignored.
				-> The new note is added at the bottom of the chord so strum
					will work properly.
			"""
				
			dupn = None
			if self.crDupRoot:
				root = tb.chord.rootNote + self.crDupRoot
				t = root + self.octave[sc] + gbl.transpose
				if t >=0 and t < 128:
					dupn = tb.chord.rootNote + self.crDupRoot

			strumAdjust = self.strum[sc] 
			strumOffset = 0
			if strumAdjust and self.direction[sc]=='DOWN':
				strumOffset += strumAdjust * tb.chord.noteListLen
				strumAdjust = -strumAdjust
				
			
			loo =zip(tb.chord.noteList, vols)	# do notes in order
			if dupn:
				loo.insert(0, [dupn, max(vols)] )
				
			loo.sort()				# mainly for strum
			for note, v in loo:
				v = self.adjustVolume( v,  p.offset)
				if not v:
					continue

			
				gbl.mtrks[self.channel].addPairToTrack(p.offset+strumOffset,
					 self.rTime[sc],
					 self.getDur(p.duration),
					 self.adjustNote(note),
					 v, unify )


				if self.duplicate[sc]:
					n = self.adjustNote(note) + self.duplicate[sc]
					if n>=0 and n<128:
						gbl.mtrks[self.channel].addPairToTrack(p.offset,
							self.rTime[sc],
							self.getDur(p.duration),
							n,	v, unify )

				
				strumOffset += strumAdjust
				
			tb.chord.reset()	# important, other tracks chord object
	
		# Adjust the voicingMove counter at the end of the bar
		
		if self.voicing.bcount:
				self.voicing.bcount -= 1
				


