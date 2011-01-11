
# MMAlyric.py

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
from MMAcommon  import *
	
class Lyric:

	textev = None	# set if TEXT EVENTS (not recommended)
	barsplit = None	# set if lyrics NOT split into sep. events for bar
	versenum = 1	# current verse number of lyric

	pushedLyrics = []
	
	def __init__(self):
		pass
		

			
	def option(self, ln):
		""" Set a lyric option. """
	
		for i, l in enumerate(ln):
			l=l.upper()
			
			if l.upper()=="SET":
				
				if i>=len(ln):
					s=''
				else:
					s=' '.join(ln[i+1:]).strip()

				if not s.startswith('['):
					s = '[' + s + ']'
		
				self.pushedLyrics.append(s)
				
				break
	

			if l.count('=') != 1:
				error("Lyric options must be in CMD=VALUE pairs.")
				
			
			a,v = l.split('=')
			
			if a == 'EVENT':
				if v == 'TEXT':
					self.textev = 1
					warning ("Placing LYRICS as TEXT EVENTS "
						"is not recommended.")
		
				elif v == 'LYRIC':
					self.textev = None
					if gbl.debug:
						print "Lyrics set as LYRIC events."

				else:
					error("Valid options for Lyric Event are TEXT or LYRIC.")
			
			elif a == 'SPLIT':
				if v == 'BAR':
					self.barsplit = 1
					if gbl.debug:					
						print "Lyrics distributed thoughout bar."
					
				elif v == 'NORMAL':
					self.barsplit = None

				else:
					error("Valid options for Lyric Split are BAR or NORMAL.")

				if gbl.debug:					
						print "Lyrics appear as one per bar."

			
			elif a == 'VERSE':
			
				if v.isdigit():
					self.versenum = int(v)

				elif v == 'INC':
					self.versenum += 1
					
				elif v == 'DEC':
					self.versenum -= 1
					
				else:
					error("Valid options of Lyric Verse are "
						"<nn> or INC or DEC.")
		
				if self.versenum < 1:
					error("Attempt to set Lyric Verse to %s. Values "
						"must be > 0." % self.versenum)

				if gbl.debug:
					print "VerseNumber set to %s" % self.versenum

					
			else:
				error("Usage: Lyric expecting EVENT, SPLIT, VERSE or SET, "
					"not '%s'"  % a )
				

	def leftovers(self):
		""" Just report leftovers on stack."""
		
		if self.pushedLyrics:
			warning("Lyrics remaining on stack.")
			
	def extract(self, ln, barNum, rpt):
		""" Extract lyric info from a chord line and place in
				META track.
				
			Returns line and lyric as 2 strings. The lyric is
				returned for debugging and has been inserted
				already so could be ignored.
		"""

		if self.pushedLyrics:
			if ln.count('[') or ln.count(']'):
				error("Lyrics not permitted inline and as LYRIC SET")
				
			ln = ln + self.pushedLyrics.pop(0)
			
		a=ln.count('[')
		b=ln.count(']')
				
		if a != b:
			error("Mismatched []s for lyrics found in chord line.")	
			
		if not a:
			return (ln, [])

		lyrics = []

		if rpt > 1:
			error("Bars with both repeat count "
				"and lyrics are not permitted.")

		ln, lyrics = pextract(ln, '[', ']')
	
		v=self.versenum
		
		if len(lyrics) == 1:
			v=1

		if v > len(lyrics):
			lyrics = ''
		else:
			lyrics=lyrics[v-1]			
		
		lyrics=lyrics.replace('\\r', ' \\r ')
		lyrics=lyrics.replace('\\n', ' \\n ')
		lyrics=lyrics.replace('  ', ' ')
	 
		if self.textev:
			lyrics = [lyrics]
		else:
			lyrics = lyrics.split()
	
		if not len(lyrics):
			return (ln, [])
			
		beat = 0
		beatAdjust = gbl.QperBar / float(len(lyrics))
			
		for t, a in enumerate(lyrics):
			a,b = pextract(a, '<', '>', 1)

			if b and b[0]:
				beat = stof(b[0], "Expecting value in <%s> in lyric." % b)
				if beat < 1  or beat > gbl.QperBar+1:
					error("Offset in lyric <> must be 1 to %s." % gbl.QperBar)
				beat -= 1
				beatAdjust = (gbl.QperBar-beat)/float((len(lyrics)-t))

			a = a.replace('\\r', '\r')
			a = a.replace('\\n', '\n')

			if a and a != ' ':
				if not a.endswith('-'):
					a += ' '
						
				p=getOffset(beat * gbl.BperQ)
				if self.textev:
					gbl.mtrks[0].addText(p, a)
				else:
					gbl.mtrks[0].addLyric(p, a)

			beat += beatAdjust
				
		return (ln, lyrics)	
	

# Create a single instance of the Lyric Class.

lyric = Lyric()

