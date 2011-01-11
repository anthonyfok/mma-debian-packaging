# MMAopts.py

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
	



import getopt
import sys
import MMAglobals;  gbl = MMAglobals
from MMAcommon import *
import MMAdocs

def opts():
	""" Option parser. """
	
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:],
			"dpsrwneom:f:M:cgGvD:", [] )


	except getopt.GetoptError:
		usage()

	for o,a in opts:
		if o == '-d':
			gbl.debug = 1

		elif o == '-o':
			gbl.showFilenames = 1

		elif o == '-p':
			gbl.pshow = 1

		elif o == '-s':
			gbl.seqshow = 1

		elif o == '-r':
			gbl.showrun = 1

		elif o == '-w':
			gbl.noWarn = 1

		elif o == '-n':
			gbl.noOutput = 1

		elif o == '-e':
			gbl.showExpand = 1

		elif o == '-c':
			gbl.chshow = 1

		elif o == '-f':
			gbl.outfile = a

		elif o == '-g':
			gbl.makeGrvDefs = 1
			
		elif o == '-G':
			gbl.makeGrvDefs = 2			

		elif o == '-m':
			try:
				a=int(a)
			except:
				error("Expecting -m arg to be a integer")
			gbl.maxBars = a

		elif o == '-v':
			print "%s" % gbl.version
			sys.exit(0)
		
		elif o == '-M':
			if a in ['0', '1']:
				gbl.cmdSMF = a
			else:
				error("Only a '0' or '1' is permitted for the -M arg.")
			
		elif o == '-D':
			if a == 'x':
				gbl.docs = 1
				
			elif a == 'n':
				import MMAchords
				MMAchords.docs()
				sys.exit(0)
										
			elif a == 'da':
				MMAdocs.docDrumNames("a")
				sys.exit(0)
			
			elif a == 'dm':
				MMAdocs.docDrumNames("m")
				sys.exit(0)
						
			elif a == 'ia':
				MMAdocs.docInstNames("a")
				sys.exit(0)
				
			elif a == 'im':
				MMAdocs.docInstNames("m")
				sys.exit(0)

			elif a == 'ca':
				MMAdocs.docCtrlNames("a")
				sys.exit(0)
				
			elif a == 'cm':
				MMAdocs.docCtrlNames("m")
				sys.exit(0)

			else:
				print "Unknown argument for -D"
				usage()

	
		else:
			usage()	  # unreachable??

	if args:
		if gbl.infile:
			usage("Only one input filename is permitted.")
		gbl.infile = args.pop(0)
		

def usage(msg=''):
	""" Usage message. """
			
	txt=[
		"MMA - Musical Midi Accompaniment",
		"  Copyright 2003-4, Bob van der Poel. Version %s" % gbl.version ,
		"  Distributed under the terms of the GNU Public License.",
		"  Usage: mma [opts ...] INFILE [opts ...]",
		"",
		"Options:",		
		" -d    Enable LOTS of debugging messages",
		" -p    Display patterns as they are defined",
		" -s    Display sequence info during run",
		" -r    Display running progress",
		" -w    Disable warning messages",
		" -n    Disable generation of midi output",
		" -e    Show parsed/expanded lines",
		" -c    Display default channel assignments",
		" -m<x> Set maxBars (default == 500)",
		" -o    Show complete filenames when opened",
		" -g    update Groove dependency database",
		" -G    create Groove dependency database",
		" -M<x> set SMF to 0 or 1",
		" -v    Display version number",
		" -D<> Extract documentation",
		"    <x>  extract doc blocks from file",
		"    <n>  Note/chord table",
		"    <dm> Midi drum names (by MIDI value)",
		"    <da> Midi drum names (alphabetical)",
		"    <im> Inst. names (by MIDI value)",
		"    <ia> Inst. names (alphabetical)",
		"    <cm> Controller names (by value)",
		"    <ca> Controller names (alphabetical)",
		" -f<file>  Set output Filename"	]

	for a in txt:
		print a		
			
	if msg:
		print
		print msg
			
	print
	sys.exit(1)
	

