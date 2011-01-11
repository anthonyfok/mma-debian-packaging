
# MMAcommon.py

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
	
	
	These are a collection of miscellaneous routines used in various
	parts of mma. It is safe to load the whole works with:
	
		from MMAcommon import *
		
	without side effects (yeah, right).

"""

from random import randrange
import MMAglobals;  gbl = MMAglobals

class struct:
	pass

def error(msg):
	""" Print an error message and exit.
	
	If the global line number is >=0 then print the line number
	as well.

	"""
	import sys
	
	ln = "ERROR:"
	
	if gbl.lineno >=0:
		ln += "<Line %d>" % gbl.lineno

	if gbl.inpath:
		ln += "<File:%s>\n   " % gbl.inpath.fname
	
	ln += " " + msg				

	print ln
	
	sys.exit(1)


def warning(msg):
	""" Print warning message and return. """
		

	if gbl.noWarn:
		return
		
	if gbl.lineno >=0:
		ln = "<Line %d>" % gbl.lineno
	else:
		ln = ''
		
	print "Warning:%s %s" % (ln, msg)

	

def getOffset(ticks, ran=None):
	""" Calculate a midi offset into a song. 
	
		Note, ticks might be a FLOAT, but the return MUST be INT,
		so don't take out the cast!
	"""
		
	p = gbl.tickOffset + ticks

	if ran:
		p += randrange( -ran, ran+1 ) 
		
	return int(p)
	


def stoi(s, errmsg=None):
	""" string to integer. """

	try:
		return int(s, 0)
	except:
		if not errmsg:
			errmsg = "Expecting integer value, not %s" % s
		error(errmsg)

def stof(s, errmsg):
	""" String to floating point. """
	
	try:
		return float(s)
	except:
		error(errmsg)



def keyLookup(d, v):
	""" Return a dict key for a value. """
	
	for a, i in d.items():
		if v==i:
			return a
	return ''


_noteLenTable = {
	'0':	1,				# special 0==1 midi tick
	'1': gbl.BperQ * 4,		# whole note
	'2': gbl.BperQ * 2,		# 1/2
	'4': gbl.BperQ,			# 1/4
	'8': gbl.BperQ / 2,		# 1/8
	'16': gbl.BperQ / 4,	# 1/16
	'32': gbl.BperQ / 8,	# 1/32
	'64': gbl.BperQ / 16,	# 1/64
	'3': gbl.BperQ/3 }		# 1/8 triplet

def getNoteLen(n):	
	""" Convert a Note to a midi tick length. 
	
		Notes are 1==Whole, 4==Quarter, etc.
		Notes can be dotted or double dotted.
		Notes can be combined: 1+4 == 5 beats, 4. or 4+8 == dotted 1/4
	"""
	
	l = 0
	for a in str(n).split('+'):
		if a.endswith('..'):
			dot = 2
			a=a[:-2]
		elif a.endswith('.'):
			dot = 1
			a=a[:-1]
		else:
			dot = 0

		try:
			i = _noteLenTable[a]						
		except:
			error("Unknown note duration %s" % n )

		if dot == 2:
			i += i/2 + i/4
		elif dot == 1:
			i += i/2
		l += i
		
	return l



def printList(l):
	""" Print each item in a list. Works for numeric and string."""
	
	for a in l:
		print a,
	print



def pextract(s, open, close, onlyone=None):
	""" Extract a parenthesized set of substrings.
	
		s     - original string
		open  - substring start tag
		close - substring end tab
		
		open/close can be multiple char strings (ie. "<<" or "-->")
		
		returns ( original sans subs, [subs, ...] )
		
	eg: pextract( "x{123}{666}y", '{',  '}' )
		Returns:  ( 'xy', [ '123', '666' ] )
	
	
	"""
		
	subs =[]
	while 1:	
		lstart=s.find(open)
		lend=s.find(close)
	
		if lstart>-1 and lstart < lend:
			subs.append( s[lstart+len(open):lend] )
			s = s[:lstart] + s[lend+len(close):]
			if onlyone:
				break
		else:
			break

	return s.strip(), subs
	
