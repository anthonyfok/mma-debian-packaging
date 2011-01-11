
# MMApatSolo.py

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
from MMAharmony import harmonize
from MMApat import PC
import MMAalloc 


class Melody(PC):
	""" The melody and solo tracks are identical, expect that
		the solo tracks DO NOT get saved in grooves and are only
		initialized once.
	"""
	
	vtype = 'MELODY'
	drumType = None
	mallet = 0	
	malletDecay = 0
	endTilde = []
			
	def setDrumType(self):
		""" Set this track to be a drum track. """
		
		if self.channel:
			error("You cannot change a track to DRUM once it has been used.")

		self.drumType = 1
		self.setChannel('10')
		
	
	""" These are replacement funcs from the parent class. They overide
		the normal pattern/solo setting routines. Note that the only
		valid routine is setRiff(). 
	"""

	def setRiff(self, ln):
		if self.riff and not self.disable:
			warning("%s: Overwriting unused melody/solo" % self.name)
			self.riff=[]
			
		self.riff.append(ln)
		
	def setMultiRiff(self, ln):
		self.riff.append(ln)
			
	def definePattern(self, name, ln):
		error("Melody/solo patterns cannot be defined.")
	

	def setMallet(self, ln):
		""" Mallet (repeat) settings. """
		
		for l in ln:
			try:
				mode, val = l.upper().split('=')
			except:
				error("Each Mallet option must contain a '=', not '%s'" % l)		
			if mode == 'RATE':
				self.mallet = getNoteLen(val)

			elif mode == 'DECAY':
				val = stof(val, "Mallet Decay must be a value, not '%s'." % val)

				if val < -20 or val > 20:
					error("Mallet Decay rate must be -20..+20")
				
				self.malletDecay = val/100

	
		if gbl.debug:
			print "%s Mallet Rate:%s Decay:%s " % \
				(self.name, self.mallet, self.malletDecay)
			

	def getLine(self, pat, ctable):
		""" Extract a melodyline for solo/melody tracks.
		
			This is only called from trackbar(), but it's nicer
			to isolate it here..
		"""
		
		sc = self.seq		
		barEnd = gbl.BperQ*gbl.QperBar

		""" We maintain a keysig table. There is an entry for each note,
			either -1,0,1 corresponding to flat,natural,sharp. We populate
			the table for each bar from the keysig value. As we process
			the bar data we update the table. There is one flaw here---in
			real music an accidental on a note in a give octave does not
			affect the following same-named notes in different octaves.
			In this routine IT DOES. 
		"""
		
		acc = {'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0, 'g':0}

		if gbl.keySig[0]=='b':
			for a in range(gbl.keySig[1]):
				acc[ ['b','e','a','d','g','c','f'][a] ] = -1
				
		if gbl.keySig[0]=='#':
			for a in range(gbl.keySig[1]):
				acc[ ['f','c','g','d','a','e','b'][a] ] = 1

		# list of notename to midivalues
		
		midiNotes = {'c':0, 'd':2, 'e':4, 'f':5, 'g':7, 'a':9, 'b':11 }

		""" The initial string is in the format "1ab;4c;;4r;". The trailing
			';' is important and needed. If we don't have this requirement
			we can't tell if the last note is a repeat of previous. For
			example, if we have coded "2a;2a;" as "2a;;" and we didn't
			have the 'must end with ;' rule, we end up with "2a;" and
			then we make this into 2 notes...or do we.
		"""


		if not pat.endswith(';'):
			error("All Solo strings must end with a ';'")

	
		""" Take our list of note/value pairs and decode into
			a list of midi values. Quite ugly.
		"""

		length = getNoteLen('4')	# default note length
		lastc = ''			# last parsed note
		velocity=self.adjustVolume( self.volume[sc], -1 ) 
		harmony = self.harmony[sc]
		harmOnly = self.harmonyOnly[sc]
		
		notes={}
		
		if self.drumType:
			isdrum =1
		else:
			isdrum = None
		
		pat = pat.replace(' ', '').split(';')[:-1]

		offset = 0

		if pat[0].startswith("~"):
			pat[0]=pat[0][1:]
			if not self.endTilde or self.endTilde[1] != gbl.tickOffset:
				error("Previous line did not end with '~'.")
			else:
				offset = self.endTilde[0] * gbl.BperQ

		self.endTilde = []

		if pat[-1].endswith("~"):
			self.endTilde = [1, gbl.tickOffset + (gbl.BperQ * gbl.QperBar) ]
			pat[-1]=pat[-1][:-1]  # strip trailing ~

		for a in pat:
			if a == '<>':
				continue

			if offset >= barEnd:
				error("Attempt to start a Solo note '%s' after end "
						"of bar." % a)
	
			# strip out all '<volume>' setting and adjust velocity
			
			a, vls = pextract(a, "<", ">")
			if vls:
				if len(vls) > 1:
					error("Only 1 volume string is permitted per note-set")
		
				vls = vls[0].upper().strip()
				if not vls in gbl.vols:
					error("%s string Expecting a valid volume, not '%s'" % \
						(self.name, vls))
				velocity=self.adjustVolume(gbl.vols[vls], -1)
		
						
			""" Split the chord chunk into a note length and notes. Each
				part of this is optional and defaults to the previously
				parsed value.
			"""
			
			i = 0
			while i < len(a):
				if not a[i] in '123468.+':
					break
				else:
					i+=1
				
			if i:
				l=getNoteLen(a[0:i])
				c=a[i:]
			else:
				l=length
				c=a

			if not c:
				c=lastc
				if not c:
					error("You must specify the first note in a solo line")

			length = l	# set defaults for next loop
			lastc = c
			
			
			""" Convert the note part into a series of midi values
				Notes can be a single note, or a series of notes. And
				each note can be a letter a-g (or r), a '#,&,n' plus
				a series of '+'s or '-'s. Drum solos must have each
				note separated by ','s: "Snare1,Kick1,44".
			"""
				
			if isdrum:
				c=c.split(',')
			else:
				c=list(c)
				

			while c:
				
				# Parse off note name or 'r' for a rest
		
				name = c.pop(0)
				
				if name == 'r':
					if offset in notes or c:
						error("You cannot combine a rest with a note in "
							"a chord for solos.")
					break;	# nothing left in chord!

				if not isdrum:
					if not name in midiNotes:
						error("%s encountered illegal note name '%s'."
							% (self.name, name))

					v = midiNotes[ name ] 

					# Parse out a "#', '&' or 'n' accidental.
				
					if c and c[0]=='#':
						c.pop(0)
						acc[name] = 1
					elif c and c[0]=='&':
						c.pop(0)
						acc[name] = -1
					elif c and c[0]=='n':
						c.pop(0)
						acc[name] = 0
						
					v+=acc[name]
				
					# Parse out +/- (or series) for octave
				
					if c and c[0] == '+':
						while c and c[0] == '+':
							c.pop(0)
							v+=12
					elif c and c[0] == '-':
						while c and c[0] == '-':
							c.pop(0)
							v-=12
									
				else:
					if not name:		# just for leading '.'s
						continue
						
					if name.isdigit():
						v=stoi(name, "Drum tones must be values")
						if v < 0 or v > 127:
							error("Drum tones must be 0..127")
					
					else:
						v = MMAmidi.drumToValue(name)
						if v == -1:
							error("Unknown drum tone '%s'" % name)

				if not offset in  notes:
					nry=notes[offset]=struct()
					nry.dur=l
					nry.velocity=self.adjustVolume(velocity, offset)
					nry.nl=[]
				notes[offset].nl.append(v)
						
				
			if harmony and offset in notes and not isdrum:
				ary=notes[offset]
				if len(ary.nl)==1:
					tb = self.getChordInPos(offset, ctable)
					if not tb.chordZ:
						h = harmonize(harmony, ary.nl[0], tb.chord.bnoteList)
						if harmOnly:
							ary.nl = h
						else:
							ary.nl.extend(h)


			offset += length

			if offset > barEnd:
				t=(offset-barEnd)/gbl.BperQ
				if self.endTilde:
					self.endTilde[0]=t
				else:
					warning("%s, end of last note overlaps end of bar by %s "
						"beat(s)." % (self.name, t))
	
		if self.endTilde and offset <= barEnd:
			error("Tilde used at end of bar which doesn't overlap next bar.")

		return notes
		
	
	def trackBar(self, pat, ctable):
		""" Do the solo/melody line. Called from self.bar() """

		notes = self.getLine(pat, ctable)

		sc=self.seq
		unify = self.unify[sc]		
		
		rptr = self.mallet
						
		k=notes.keys()
		k.sort()

		for offset in k:
			ary=notes[offset]
			l=ary.dur
			v=ary.velocity
			for n in ary.nl:

				if not self.drumType:		# octave, transpose
					n = self.adjustNote(n)
				if rptr and l>rptr:
					ll = self.getDur(rptr)
					offs = 0
					vel = v

					for q in range(l/rptr):
						gbl.mtrks[self.channel].addPairToTrack( offset + offs,
							self.rTime[sc], ll, n, vel, unify )
						offs += rptr
						if self.malletDecay:
							vel = int( vel + (vel * self.malletDecay) )
							if vel<1: vel = 1
							if vel>255: vel=255

				else:
					gbl.mtrks[self.channel].addPairToTrack( offset,
						self.rTime[sc], self.getDur(l), n, v, unify )
			

			


class Solo(Melody):
	""" Pattern class for a solo track. """

	vtype = 'SOLO'	
	
	
	# Grooves are not saved/restored for solo tracks.
	
	def restoreGroove(self, gname):
		self.setSeqSize()
		
	def saveGroove(self, gname):
		pass
	


#######################

""" When solos are included in a chord/data line they are 
	assigned to the tracks listed in this list. Users can
	change the tracks with the setAutoSolo command.
"""

autoSoloTracks = [ 'SOLO', 'SOLO-1', 'SOLO-2', 'SOLO-3' ]

def copySoloToHarmony():
	if len(autoSoloTracks) < 2: return
	trk=autoSoloTracks[0]
	if not trk: return
	if not gbl.tnames.has_key(trk): return
	if gbl.tnames[trk].riff == []: return
	
	riff = gbl.tnames[trk].riff[0]

	for t in autoSoloTracks[1:]:
		if gbl.tnames.has_key(t) 	\
				and gbl.tnames[t].riff == [] \
				and max(gbl.tnames[t].harmonyOnly):
			gbl.tnames[t].riff.append(riff)
			if gbl.debug:
				print "Riff from %s copied to %s for HarmonlyOnly." % (trk, t)
			
	
def setAutoSolo(ln):
	""" Set the order and names of tracks to use when assigning
		automatic solos (specified on chord lines in {}s).
	"""
	
	global autoSoloTracks
	
	if not len(ln):
		error("You must specify at least one track for autosolos.")
		
	autoSoloTracks = []
	for n in ln:
		n=n.upper()
		MMAalloc.trackAlloc(n, 1)
		if gbl.tnames[n].vtype not in ('MELODY', 'SOLO'):
			error("All autotracks must be Melody or Solo tracks, "
				"not %s." % gbl.tnames[n].vtype)
	
		autoSoloTracks.append(n)

	if gbl.debug:
		print "AutoSolo track names:",
		for a in autoSoloTracks:
			print a,
		print		
				

def extractSolo(ln, rptcount):
	""" Parser calls this to extract solo strings. """

	a = ln.count('{')
	b = ln.count('}')
	
	if a != b:
		error("Mismatched {}s for solo found in chord line.")
		
	if not a:
		return (ln, [])

	if rptcount > 1:
		error("Bars with both repeat count and solos are not permitted.")

	ln, solo = pextract(ln, '{', '}')

	if len(solo) > len(autoSoloTracks):
		error("Too many melody/solo riffs in chord line. %s used, "
				"only %s defined." % (len(solo), len(autoSoloTracks)) )
				
	for s, trk in zip(solo, autoSoloTracks):
		MMAalloc.trackAlloc(trk, 1)		
		gbl.tnames[trk].setRiff( s.strip() )

	return (ln, solo)
		
