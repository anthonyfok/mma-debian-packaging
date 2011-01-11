
# MMAchords.py
	
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

"""
	Table of chords. All are based on a C scale.
	Generating chords is easy in MIDI since we just need to
	add/subtract constants, based on yet another table.
	
	CAUTION, if you add to this table make sure there are at least
	3 notes in each chord! Don't make any chord longer than 8 notes
	(The pattern define sets volumes for only 8).
		
	There is a corresponding scale set for each chord. These are
	used by bass and scale patterns.
	
	Each chord needs an English doc string. This is extracted by the
	-Dn option to print a table of chordnames for inclusion in the
	reference manual.
		
"""


_chords = {
	'M':	((0,    4,    7 ),
			 (0, 2, 4, 5, 7, 9, 11),
			 "Major triad. This is the default and is used in  "
			 "the absense of any other chord type specification."),

	'm':	((0,    3,    7 ),
			 (0, 2, 3, 5, 7, 9, 11),
			 "Minor triad."),

	'mb5':	((0,    3,    6 ),
			 (0, 2, 3, 5, 6, 9, 11),
			 "Minor triad with flat 5th."),

	'm#5':	((0,    3,    8 ),
			 (0, 2, 3, 5, 8, 9, 11),
			 "Major triad with augmented 5th."),

	'm6':	((0,    3,    7, 9 ),
			 (0, 2, 3, 5, 7, 9, 11),
			 "Minor 6th."),

	'm7':	((0,    3,    7,    10 ),
			 (0, 2, 3, 5, 7, 9, 10),
			 "Minor 7th."),

	'mM7':	((0,    3,    7,    11 ),
			 (0, 2, 3, 5, 7, 9, 11),
			 "Minor Triad plus Major 7th. You will also see this printed "
			 "as ``m(maj7)'', ``m+7'', ``min(maj7)'' and ``min$\sharp$7'' "
			 "(which \mma\ accepts); as well as the \mma\ \emph{invalid} "
			 "forms: ``-($\Delta$7)'', and ``min$\\natural$7''."),

	'm7b5':	((0,    3,    6,    10 ),
			 (0, 2, 3, 5, 6, 9, 10),
			 "Minor 7th, flat 5 (aka 1/2 diminished). "),

	'm7b9':	((0,    3,    7,    10, 13 ),
			 (0, 2, 3, 5, 7, 9, 10),
			 "Minor 7th with added flat 9th."),

	'7':	((0,    4,    7,    10 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th."),

	'7#5':	((0,    4,    8,    10 ),
			 (0, 2, 4, 5, 8, 9, 10),
			 "7th, sharp 5."),

	'7b5':	((0,    4,    6,    10 ),
			 (0, 2, 4, 5, 6, 9, 10),
			 "7th, flat 5."),

	'dim':	((0,    3,    6,    9 ),
			 (0, 2, 3, 5, 6, 8, 9 ),	# missing 8th note
			 "Diminished. \mma\ assumes a diminished 7th."),

	'aug':	((0,    4,    8 ),
			 (0, 2, 4, 5, 8, 9, 11 ),
			 "Augmented triad."),

	'6':	((0,    4,    7, 9 ),
			 (0, 2, 4, 5, 7, 9, 11),
			 "Major tiad with added 6th."),

	'M7':	((0,    4,    7,    11),
			 (0, 2, 4, 5, 7, 9, 11),
			 "Major 7th."),

	'M7b5':	((0,    4,    6,    11 ),
			 (0, 2, 4, 5, 6, 9, 11 ),
			 "Major 7th with a flatted 5th."),

	'sus4':	((0,    5,    7 ),
			 (0, 2, 5, 5, 7, 9, 11),
			 "Suspended 4th, major triad with 3rd raised half tone."),

	'7sus':	((0   , 5,    7,    10 ),
			 (0, 2, 5, 5, 7, 9, 10),
			 "7th with suspended 4th, dominant 7th with 3rd "
			 "raised half tone."),

	'sus2':	((0,    2,    7 ),
			 (0, 2, 2, 5, 7, 9, 11),
			 "Suspended 2nd, major triad with major 2nd above "
			 "root substituted for 3rd."),

	'7sus2':((0,    2,    7,    10 ),
			 (0, 2, 2, 5, 7, 9, 10),
			 "A sus2 with dominant 7th added."),

	'9':	((0,    4,    7,    10, 14 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th plus 9th."),

	'sus9':	((0,    4,    7,    14),
			 (0, 2, 4, 5, 7, 9, 14),
			 "Dominant 7th plus 9th, omit 7th."),

	'9b5':	((0,    4,    6,    10, 14 ),
			 (0, 2, 4, 5, 6, 9, 10),
			 "Dominant 7th plus 9th with flat 5th."),

	'm9':	((0,    3,    7,    10, 14 ),
			 (0, 2, 3, 5, 7, 9, 10),
			 "Minor triad plus 7th and 9th."),

	'm9b5':	((0,    3,    6,    10, 14 ),
			 (0, 2, 3, 5, 6, 9, 10),
			 "Minor triad, flat 5, plus 7th and 9th."),

	'm(sus9)':((0,    3,    7,    14 ),
			   (0, 2, 3, 5, 7, 9, 14),
			 "Minor triad plus 9th (no 7th)."),

	'M9':	((0,    4,    7,    11, 14 ),
			 (0, 2, 4, 5, 7, 9, 11),
			 "Major 7th plus 9th."),

	'7b9':	((0,    4,    7,    10, 13 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th with flat 9th."),

	'7#9':	((0,    4,    7,    10, 15 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th with sharp 9th."),

	'7b5b9':((0,    4,    6,    10, 13 ),
			 (0, 2, 4, 5, 6, 9, 10),
			 "Dominant 7th with flat 5th and flat 9th."),

	'7b5#9':((0,    4,    6,    10, 15 ),
			 (0, 2, 4, 5, 6, 9, 10),
			 "Dominant 7th with flat 5th and sharp 9th."),

	'7#5#9':((0,    4,    8,    10, 15 ),
			 (0, 2, 4, 5, 8, 9, 10),
			 "Dominant 7th with sharp 5th and sharp 9th."),

	'7#5b9':((0,    4,    8,    10, 13 ),
			 (0, 2, 4, 5, 8, 9, 10),
			 "Dominant 7th with sharp 5th and flat 9th."),

	'aug7':	((0,    4,    8,    10 ),
			 (0, 2, 4, 5, 8, 9, 10),
			 "An augmented chord (raised 5th) with a dominant 7th."),

	'aug7b9':((0,    4,    8,    10, 13 ),
			  (0, 2, 4, 5, 8, 9, 10),
			 "Augmented 7th with flat 5th and sharp 9th."),

	'11':	((0,    4,    7,    10, 14, 17 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "9th chord plus 11th."),

	'm11':	((0,    3,    7,    10, 14, 17 ),
			 (0, 2, 3, 5, 7, 9, 10),
			 "9th with minor 3rd,  plus 11th."),

	'11b9':	((0,    4,    7,    10, 13, 17 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "9th chord plus flat 11th."),

	'9#5':	((0,    4,    8,    10, 14 ),
			 (0, 2, 4, 5, 8, 9, 10),
			 "Dominant 7th plus 9th with sharp 5th."),

	'9#11':	((0,    4,    7,    10, 15, 18 ),
			 (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th plus 9th and sharp 11th."),

	'7#9#11':((0,    4,    7,    10, 15, 18 ),
			  (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th plus sharp 9th and sharp 11th."),

	'M7#11':((0,    4,    7,    11, 14, 18 ),
			 (0, 2, 4, 5, 7, 9, 11),
			 "Major 7th plus 9th and sharp 11th."),
	
	# these two chords should probably NOT have the 5th included,
	# but since a number of voicings depend on the 5th being
	# the third note of the chord, they're here.
	
	'13':	((0,    4   , 7,    10, 21),
			 (0, 2, 4, 5, 7, 9, 10),
			 "Dominant 7th (including 5th) plus 13th."),

	'M13':	((0,    4,    7,    11, 21),
			 (0, 2, 4, 5, 7, 9, 11),
			 "Major 7th (including 5th) plus 13th.") 
}

_chordsSyn = {
	'm+5':		'm#5'  ,
	'm7-5':     'm7b5',
	'+':		'aug'  ,
	'7-9':      '7b9'  ,
	'7+9':      '7#9'  ,
	'maj7':		'M7'   ,
	'7sus4':	'sus4' ,
	'7#11':		'9#11' ,
	'7+':		'aug7' ,
	'7+5':      '7#5'  ,
	'7-5':      '7b5'  ,
	'sus':		'sus4' ,
	'm(maj7)':	'mM7'  ,
	'm+7':		'mM7'  ,
	'min(maj7)':'mM7'  ,
	'min#7':	'mM7'  ,
	'dim7':     'dim'
}


"""
	Table of chord adjustment factors. Since the initial chord is based
	on a C scale, we need to shift the chord for different degrees. Note,
	that with C as a midpoint we shift left for G/A/B and right for D/E/F.
	
	Should the shifts take in account the current key signature?
"""
	
_chordAdjust = {
	'A':-3,   'A#':-2,   'Ab':-4,  
	'B':-1,   'B#': 0,   'Bb':-2,  
	'C': 0,   'C#': 1,   'Cb':-1,  
	'D': 2,   'D#': 3,   'Db': 1,  
	'E': 4,   'E#': 5,   'Eb': 3,  
	'F': 5,   'F#': 6,   'Fb': 4,  
	'G':-5,   'G#':-4,   'Gb':-6 }
		


###############################
# Chord creation/manipulation #
###############################

class ChordNotes:
	"""
	The Chord class creates and manipulates chords for MMA. The
	class is initialized with a call with the chord name. Eg:
	
		ch = ChordNotes("Am")
		
	The following methods and variables are defined:

		noteList  - the notes in the chord as a list. The "Am"
                     would be [9, 12, 16].
			
		noteListLen  - length of noteList.

		tonic      - the tonic of the chord ("Am" would be "A").
		
		chordType  - the type of chord ("Am" would be "m").
		
		rootNote   - the root note of the chord ("Am" would be a 9).

		bnoteList  - the original chord notes, bypassing any
                     invert(), etc. mangling.
			
		scaleList  - a 7 note list representing a scale similar to
		             the chord.
		             
		reset() - resets noteList to the original chord notes.
		    This is useful to restore the original after
			chord note mangling by invert(), etc. without having to
			create a new chord object.
			
				
		invert(n) - Inverts a chord by 'n'. This is done inplace and
			returns None. 'n' can have any integer value, but -1 and 1
			are most common. The order of the notes is not changed. Eg:
				
				ch=Chord('Am') 
				ch.noteList == [9, 12, 16]
				ch.invert(1)
				ch.noteList  = [21, 12, 16]				
			
		compress() - Compresses the range of a chord to a single octave. This is
			done inplace and return None. Eg:
		 	
 		 		ch=Chord("A#13")
		 		ch.noteList == [1, 5, 8, 11, 22]
		 		ch.compress()
		 		ch.noteList == [1, 5, 8, 11, 10 ]
		 		
		 		
		limit(n) - 	Limits the range of the chord 'n' notes. Done inplace
			and returns None. Eg:
			
				ch=Chord("CM7#11")
				ch.noteList == [0, 4, 7, 11, 15, 18]   
				ch.limit(4)
				ch.noteList ==  [0, 4, 7, 11]
	
		
		docs() - Prints a set of docs for inclusion in the reference manual.
			Does not return. 		
		 
	"""
	
	
	#################
	### Functions ###
	#################
	
	def __init__(self, name):
		""" Create a chord object. Pass the chord name as the only arg. 
			
			NOTE: Chord names ARE case-sensitive!
	
			The chord NAME at this point is something like 'Cm' or 'A#7'. 
			Split off the tonic and the type. 
			If the 2nd char is '#' or 'b' we have a 2 char tonic,
			otherwise, it's the first char only.
		
			Note pythonic trick: By using ranges like [1:2] we
			avoid runtime errors on too-short strings. If a 1 char
			string,  name[1] is an error; name[1:2] just returns None.
		"""
		
		if name == 'z':
			self.tonic = self.chordType = None
			self.noteListLen = 0
			self.notesList = self.bnoteList = []
			return
						
		name = name.replace('&', 'b')
		
		if name[1:2] in ( '#b' ):
			tonic = name[0:2]			
			type  = name[2:]
		else:
			tonic = name[0:1]
			type  = name[1:]

		if not type:		# If no type, make it a Major
			type='M'

		# Synonym convert
		
		if type in _chordsSyn:
			type=_chordsSyn[type]

		try:
			notes = _chords[type][0]
			adj =   _chordAdjust[tonic]
		except:
			error( "Illegal/Unknown chord in '%s'. Tonic='%s', Type='%s'" \
				% (name, tonic, type) )

		if notes[0] + adj < 0:
			adj += 12

		self.noteList    = [ x + adj for x in notes ]
		self.bnoteList   = tuple(self.noteList)
		self.scaleList   = tuple([ x + adj for x in _chords[type][1] ])
		self.chordType   = type
		self.tonic       = tonic
		self.rootNote    = self.noteList[0]
		
		self.noteListLen = len(self.noteList)


	def reset(self):
		""" Restores notes array to original, undoes mangling. """
		
		self.noteList    = list(self.bnoteList[:])
		self.noteListLen = len(self.noteList)
		
	
	def invert(self, n):
		""" Apply an inversion to a chord.
		
			This does not reorder any notes, which means that the root note of
			the chord reminds in postion 0. We just find that highest/lowest
			notes in the chord and adjust their octave.
			
			NOTE: Done on the existing list of notes. Returns None.
		"""

		if n:
			c=self.noteList[:]
		
			while n>0:		# Rotate up by adding 12 to lowest note
				n -= 1
				c[c.index(min(c))]+=12
			
			while n<0:		# Rotate down, subtract 12 from highest note
				n += 1
				c[c.index(max(c))]-=12
	
		self.notelist = c
		
		return None	



	def compress(self):
		""" Compress a chord to one ocatve."""
	

		""" Get max permitted value. This is the lowest note
			plus 12. Note: use the unmodifed value bnoteList!
		"""
	
		mx = self.bnoteList[0] + 12		
		c=[]

		for i, n in enumerate(self.noteList):
			if n > mx:
				n -= 12
			c.append(n)

		self.noteList = c
		
		return None



	def limit(self, n):
		""" Limit the number of notes in a chord. """
		
		if n < self.noteListLen:
			self.noteList =  self.noteList[:n]
			self.noteListLen = len(self.noteList)
		
		return None


	def center1(self, lastChord):
		""" Descriptive comment needed here!!!! """
		
		def minDistToLast(x, lastChord):
			dist=99
			for j in range(len(lastChord)):
				if abs(x-lastChord[j])<abs(dist):
					dist=x-lastChord[j]
			return dist

		def sign(x):
			if (x>0):
				return 1
			elif (x<0):
				return -1
			else:
				return 0			
	
		# Only change what needs to be changed compared to the last chord
		# (leave notes where they are if they are in the new chord as well).

		if lastChord:
			ch=self.noteList

			for i in range(len(ch)):
					
				# minimize distance to last chord

				oldDist = minDistToLast(ch[i], lastChord)				
				while abs(minDistToLast(ch[i] - sign(oldDist)*12,
						lastChord)) < abs(oldDist):
					ch[i] -= 12* sign(oldDist) 
					oldDist = minDistToLast(ch[i], lastChord)

		return None
		
	def center2(self, centerNote, noteRange):
		""" Need COMMENT """
		
		ch=self.noteList
		for i,v in enumerate(ch):

			dist = v - centerNote 
			if dist < -noteRange:
				ch[i] = v + 12 * ( abs(dist) / 12+1 )
			if dist > noteRange:
				ch[i] = v - 12 * ( abs(dist) / 12+1 )
		
		return None
		

def docs():
	""" Print out a list of chord names and docs in LaTex. """

	import copy
	
	# Just in case someone else wants to use _chords, work on a copy
	
	chords=copy.copy(_chords)
	
	# Add the syns into the chord table. We don't bother to
	# create notes (they're not used), but we create descriptions

	for a in _chordsSyn:
		n = "See ``%s''" % _chordsSyn[a]
		n=n.replace("#", '$\\sharp$')
		n=n.replace('b', '$\\flat$')
		chords[a]=( (),(), n)
		
	a=chords.keys()
	a.sort()
	for n in a:
		nm=n.replace("#", '$\\sharp$')
		nm=nm.replace('b', '$\\flat$')
		print "\\insline{%s}{%s}" % (nm, chords[n][2])

	



