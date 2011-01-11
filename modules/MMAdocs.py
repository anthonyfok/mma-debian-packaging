
# MMAdocs.py
	
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
import os	

	
def docDrumNames(order):
	""" Print LaTex table of drum names. """
	
	n=zip( MMAmidi.drumNames, range(27,len(MMAmidi.drumNames)+27) )

	if order == "a":
		n.sort()
		for a,v in n:
			print "\\insline{%s} {%s}" % (a, v)
			
	else:
		for a,v in n:
			print "\\insline{%s} {%s}" % (v, a)
		
def docCtrlNames(order):
	""" Print LaTex table of MIDI controller names. """
	
	n=zip( MMAmidi.ctrlNames, range(len(MMAmidi.ctrlNames)) )

	if order == "a":
		n.sort()
		for a,v in n:
			print "\\insline{%s} {%02x}" % (a, v)
			
	else:
		for a,v in n:
			print "\\insline{%02x} {%s}" % (v, a)

def docInstNames(order):
	""" Print LaTex table of instrument names. """

	n=zip( MMAmidi.voiceNames, range(len(MMAmidi.voiceNames)) )
	if order == "a":
		n.sort()
		for a,v in n:
			a=a.replace('&', '\&')
			print "\\insline{%s} {%s}" % (a, v)
			
	else:
		for a,v in n:
			a=a.replace('&', '\&')
			print "\\insline{%s} {%s}" % (v, a)


""" Whenever MMA encounters a DOC command, or if it defines
	a groove with DEFGROOVE it calls the docAdd() function.
	
	The saved docs are printed to stdout with the docDump() command.
	This is called whenever parse() encounters an EOF.
	
	Both routines are ignored if the -Dx command line option has
	not been set.
	
	Storage is done is in the following arrays.
"""

fname = ''
author=""
notes=""
defs=[]

def docAuthor(ln):
	global author
	
	author = ' '.join(ln)

	
def docNote(ln):
	""" Add a doc line. """

	global fname, notes
	
	if not gbl.docs or not ln:
		return
	
	# Grab the arg and data, save it
	
	fname = os.path.basename(gbl.inpath.fname)	
	if notes:
		notes += ' '
	notes +=  ' '.join(ln) 

	
def docDefine(ln):
	""" Save a DEFGROOVE comment string. 
	
		Entries are stored as a list. Each item in the list is
		complete groove def looking like:
			defs[ [ Name, Seqsize, Description, [ [TRACK,INST]...]] ...]

	"""
	
	global defs
		
	l = [ ln[0], gbl.seqSize, ' '.join(ln[1:]) ]
	tks = gbl.tnames.keys()
	tks.sort()
	for a in tks:
		c=gbl.tnames[a]
		if c.sequence:
			if c.vtype=='DRUM':
				v=MMAmidi.valueToDrum(c.toneList[0])
			else:
				v=MMAmidi.valueToInst(c.voice[0])
			l.append( [c.name, v ] )
		
	defs.append(l)	
				
def docDump():
	""" Print the LaTex docs. """
	
	global fname, author, notes, defs
	
	if gbl.docs:

		if notes:
			if fname.endswith(gbl.ext):
				fname='.'.join(fname.split('.')[:-1])
			print "\\filehead{%s}{%s}" % (totex(fname), totex(notes))
			notes = ""
			print
		
		if defs:
			for l in defs:
				print "  \\instable{%s}{%s}{%s}{" % \
					(totex(l[0]), totex(l[2]), l[1] )
				for c,v in l[3:]:
					print "    \\insline{%s}{%s}" % (c.title(), totex(v))
				print "  }"
			defs = {}


	author = ""
	

		
def totex(s):
	""" Parse a string and quote tex stuff. 
	
		Also handles proper quotation style.
	"""

	s = s.replace("$", "\\$")
	s = s.replace("*", "$*$")
	s = s.replace("\\", "\\\\")
	s = s.replace("#", "\\#")
	s = s.replace("&", "\\&")
	
	q="``"
	while s.count('"'):
		i=s.find('"')
		s=s[:i] + q + s[i+1:]
		if q=="``":
			q="''"
		else:
			a="``"
	
	
	return s
