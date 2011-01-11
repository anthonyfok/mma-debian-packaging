
# MMAparse.py

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
	

	This module does all file parsing. Most commands
	are passed to the track classes; however, things
	like TIME, SEQRND, etc. which just set global flags
	are completely handled here.
"""

import os
import random

import MMAglobals;  gbl = MMAglobals
from MMAchords import ChordNotes
import MMAfile
import MMAdocs
import MMAmidi
import MMAmidiIn
from MMAauto  import loadGrooveDir
from MMAalloc import trackAlloc
from MMAcommon  import *
import MMAtranslate
from MMAlyric import lyric
import MMApatSolo
from MMAmacro import macros
import MMAmdefine

def setDebugMacro(n):
	macros.vars[n] = "DEBUG=%s FILENAMES=%s PATTERNS=%s \
		SEQUENCE=%s RUNTIME=%s WARNINGS=%s EXPAND=%s" % \
		(gbl.debug, gbl.showFilenames, gbl.pshow, gbl.seqshow, \
		gbl.showrun,  int(not gbl.noWarn), gbl.showExpand)

setDebugMacro('_DEBUG')
setDebugMacro('_LASTDEBUG')

lastChord = None   # only used in mdata()
futureVol = []     # list of volume changes on (de)cresc
barNum = 0         # current bar number, for debug and MAXBAR tracking
seqRnd = 0         # set if SEQRND has been set


# This table is passed to the track classes.

class CTable:
	offset = 0		# offset of chord into bar in ticks
	chord = None
	chordZ = 0
	arpeggioZ = 0
	walkZ = 0
	drumZ = 0
	bassZ = 0
	scaleZ = 0




########################################
# File processing. Mostly jumps to pats
########################################

	
def parseFile(n):
	""" Open and process a file. Errors exit. """

	fp=gbl.inpath

	f=MMAfile.ReadFile(n)

	parse(f)
	gbl.inpath=fp

	if gbl.debug:
		print "File '%s' closed." % n



def parse(inpath):
	""" Process a mma input file. """

	gbl.inpath = inpath

	curline = None
	
	while 1:
		curline = inpath.read()
		if curline == None:
			MMAdocs.docDump()
			break	
		
		gbl.lineno = inpath.lineno
		
		l = macros.expand(curline)
			
		action = l[0].upper()
		
		if gbl.showExpand and action !='REPEAT':
			print l	
		
		# If the command is in the simple function table, jump & loop.

		if action in simpleFuncs:
			simpleFuncs[action](l[1:])
			continue

		
		""" We have several possibilities ...
			1. The command is a valid assigned track name,
			2. The command is a valid track name, but needs to be
				dynamically allocated,
			3. It's really a chord action
		"""

		if not action in gbl.tnames:
			trackAlloc(action, 0)	# ensure that track is allocated
			
		if action in gbl.tnames:	#  BASS/DRUM/APEGGIO/CHORD
	
			name = action
			if len(l) < 2:
				error("Expecting argument after '%s'" % name)
			action = l[1].upper()	

			if action in trackFuncs:
				trackFuncs[action](name, l[2:])
			else:
				error ("Don't know '%s'" % curline)
				
			continue			
			
		""" At this point we have to have a chord set. Anything else
			becomes an error condition.
			
		"""
		
		mdata(l)
		
		
#######################################
# Do-nothing functions

def comment(ln):
	pass

def repeatend(ln):
	error("Repeatend/EndRepeat without Repeat.")
	
def repeatending(ln):
	error("Repeatending without Repeat.")

def endmset(ln):
	error("EndMset/MSetEnd without If.")
	
def ifend(ln):
	error("ENDIF without IF.")

def ifelse(ln):
	error("ELSE without IF.")


#######################################
# Repeat/jumps

			
def repeat(ln):
	""" Repeat/RepeatEnd/RepeatEnding.

		Read input until a RepeatEnd is found. The entire
		chunk is pushed back into the input stream the
		correct number of times. This accounts for endings and
		nested repeats.

	"""
	
	
	def repeatChunk():
		q=[]
		qnum=[]
		nesting = 0

		while 1:
			l=gbl.inpath.read()
			gbl.lineno = gbl.inpath.lineno
			
			if not l:
				error("EOF encountered processing Repeat")
				
			act=l[0].upper()
			
			if act=='REPEAT':
				nesting += 1
			
			elif act in ('REPEATEND', 'ENDREPEAT') and nesting:
				nesting -= 1
		
			elif act == 'REPEATENDING' and nesting:
				pass
			
			elif act in ('REPEATEND', 'ENDREPEAT', 'REPEATENDING'):
				return (q, qnum, act, l[1:])
			
			q.append(l)
			qnum.append(gbl.inpath.lineno)

	stack=[]
	stacknum=[]
	main=[]
	mainnum=[]
	ending = 0

	main, mainnum, act, l = repeatChunk()

	while 1:
		if act in ('REPEATEND', 'ENDREPEAT'):
			if l:
				if len(l)>1:
					error("%s takes only one (optional) arg." % act)
				count=stoi(l[0], "%s takes an integer arg." % act)
				if count==2:
					warning("REPEATEND using default count value (2). "
						"Did you mean 3 or more?")
				if count<2:
					error("%s count must be 2 or greater." % act)
				if count>25:
					warning("%s is a large value for %s" % (count, act) )
			else:
				count=2	

			if not ending:
				count += 1
			for c in range(count-1):
				stack.extend(main)
				stacknum.extend(mainnum)
		
			gbl.inpath.push(stack, stacknum)
			break
							
		elif act == 'REPEATENDING':
			ending = 1
			if len(l) > 1:
				error("REPEATENDING only takes one (optional) arg.")
			if len(l) == 1:
				count=stoi(l[0], 
					"REPEATENDING takes an integer arg.")
				if count < 1:
					error("REPEATENDING count must be postive.")
				if count > 25:
					warning("%s is a large value for "
						"RepeatEnding" % count)
			else:
				count = 1
				
			rpt, rptnum, act, l = repeatChunk()
			
			for c in range(count):
				stack.extend(main)
				stacknum.extend(mainnum)
				stack.extend(rpt)
				stacknum.extend(rptnum)
			
			
		else:
			error("Unexpected line in REPEAT")
	


def goto(ln):
	if len(ln) != 1:
		error("Usage: GOTO Label")
	gbl.inpath.goto(ln[0].upper())

def eof(ln):
		gbl.inpath.toEof()


#######################################
# Tempo/timing


def setTime(ln):
	""" Set the 'time sig'. 
	
		We do restrict the time setting to the range of 1..12.
		No particular reason, but we do need some limit? Certainly
		it has to be greater than 0.
	"""

	if len(ln) != 1:
		error("Use: Time N.")
		
	n = stoi(ln[0], "Argument for time must be integer.")
		
	if n < 1 or n > 12:
		error("Time (beats/bar) must be 1..12.")
		
	# If no change, just ignore this.
	
	if gbl.QperBar != n:
		gbl.QperBar = int(n)
		
		# Time changes zap all predfined sequences
	
		for a in gbl.tnames.values():
			a.clearSequence()
			
	macros.vars['_TIME']=str(n)
						
	
def tempo(ln):
	""" Set tempo. """
	
	
	ln=ln[:]	# we're modifying this, work on copy
	
	emsg = "Use: Tempo [*,+,-] BperM [BARS]."

	if not ln:
		error(emsg)
	
	# Get optional modifier '*', '+' or '-'. 

	if ln[0] in '*-+':
		mod = ln.pop(0)
		if not ln:
			error(emsg)
		if mod == '*':
			mul=1
			incr = 0
		elif mod == '+':
			mul = 0
			incr = 1
		elif mod == '-':
			mul = 0
			incr = -1
	else:
		mul = 0
		incr = 0
	

	v=ln.pop(0)
	v = stof(v, "Tempo expecting value, not '%s'." % v )
	
	if mul:
		v *= gbl.tempo
	elif incr:
		v *= incr
		v += gbl.tempo 
		
	v=int(v)

	if not len(ln):		# no BARS arg == immediate tempo setting
		gbl.tempo = int(v)
		gbl.mtrks[0].addTempo(gbl.tickOffset, gbl.tempo) 
		if gbl.debug:
			print "Set Tempo to %s" % gbl.tempo
	
	else:
		bars = ln.pop(0)		# Do a tempo change over bar count 

		if ln:
			error(emsg)
			
		bars = stof(bars, "Expecting value, not %s" % bars )
		numbeats = int(bars * gbl.QperBar)

		if numbeats < 1:
			error("Beat count must be greater than 1.")
	
		# Vary the rate in the meta track
	
		tincr = (v - gbl.tempo) / float(numbeats)	# incr per beat
		bstart = gbl.tickOffset			# start
		boff = 0
		tempo = gbl.tempo

		for n in range(numbeats):
			tempo += tincr
			if tempo:
				gbl.mtrks[0].addTempo(bstart + boff, int(tempo))
			boff += gbl.BperQ
	
		if tempo != v:
			gbl.mtrks[0].addTempo(bstart + boff, int(v) )
		
		gbl.tempo = int(v)
	
		if gbl.debug:
			print "Set future Tempo to %s over %s beats" % \
				( int(tempo), numbeats)
				
	macros.vars['_TEMPO']=str(gbl.tempo)


def rtime(ln):
	""" Set random factor for note timings. """
	
	if not ln:
		error ("Use: RTime N [...].")
	
	for n in gbl.tnames:
		trackRtime(n, ln)

def rskip(ln):
	""" Set random factor for note skip. """
	
	if not ln:
		error ("Use: RSkip N [...].")
	
	for n in gbl.tnames:
		trackRskip(n, ln)


def beatAdjust(ln):
	""" Delete or insert some beats into the sequence."""

				
	if len(ln) != 1:
		error("Use: BeatAdjust  NN")
	
	adj = stof(ln[0], "Expecting a value (not %s) for BeatAdjust." % ln[0])
	adj = int(adj * gbl.BperQ)
	
	gbl.tickOffset += adj
	
	if gbl.debug:
		print "BeatAdjust: inserted %s at bar %s." % (adj, barNum + 1)
	
	
def cut(ln):
	""" Insert a all-note-off into all tracks. """
	
	if not len(ln):
		ln=['0']
			
	if len(ln) != 1:
		error("Use: Cut Offset")
		
	""" Loop though all the tracks. Note that trackCut() checks
		to make sure that there is a need to insert in specified track.
		In this loop we create a list of channels as we loop though
		all the tracks, skipping over any duplicate channels or
		tracks with no channel assigned.
	"""
	
	l=[]
	nms=gbl.tnames.keys()
	nms.sort()
	for t in nms:
		c = gbl.tnames[t].channel
		if not c or c in l:
			continue
		l.append(c)
		trackCut(t, ln)


def fermata(ln):
	""" Apply a fermata timing to the specified beat. """
	
	if len(ln) != 3:
		error("Use: Fermata 'offset' 'duration' 'adjustment'")
		
	offset = stof(ln[0], "Expecting a value (not '%s') "
				"for Fermata Offset." % ln[0] ) 
				
	if offset < -gbl.QperBar or offset > gbl.QperBar:
		warning("Fermata: %s is a large beat offset." % offset)
		
	dur = stof(ln[1], "Expecting a value (not '%s') for Fermata "
				"Duration." % ln[1])
				
	if dur <= 0:
		error("Fermata duration must be greater than 0.")
		
	if dur > gbl.QperBar:
		warning("Fermata: %s is a large duration.")
	
	adj = stof(ln[2], "Expecting a value (not '%s') for Fermata "
				"Adjustment." % ln[2])

	if adj< 100:
		warning("Fermata: Adjustment less than 100 is shortening beat value.")
		
	if adj == 100:
		error("Fermata: using value of 100 makes no difference, "
				"must be an error.")
	
	moff=int(gbl.tickOffset + (gbl.BperQ * offset))

	if moff < 0:
		error("Fermata offset comes before track start.")
	
	gbl.mtrks[0].addTempo(moff, int(gbl.tempo / (adj/100)) )

	tickDur = int(gbl.BperQ * dur)
	
	gbl.mtrks[0].addTempo(moff + tickDur, gbl.tempo)

	# Clear out NoteOn events in all tracks

	if offset < 0:
		start = moff + int(.05 * gbl.BperQ)
		end = moff + tickDur - int(.05 * gbl.BperQ)
		
		for n, tr in gbl.mtrks.items():
			if n <= 0: continue		# skip meta track
			tr.zapRangeTrack(start, end )
	
	if gbl.debug:
		print "Fermata: Beat %s, Duration %s, Change %s, Bar %s" % \
			(offset, dur, adj, barNum + 1)
		if offset < 0:
			print "\tNoteOn Events removed in tick range %s to %s" \
				% (start, end)

#######################################
# Volume
		
			
def rvolume(ln):
	""" Set random for note volumes."""
	
	if not ln:
		error ("Use: RVolume N [...].")
		
	for n in gbl.tnames:
		trackRvolume(n, ln )


def volume(ln):
	""" Set master volume. """
		
	if len(ln) != 1:
		error ("Use: Volume Dynamic [RANGE].")

	v=ln[0].upper()
	if not v in gbl.vols:
		error("Unknown volume '%s'." % ln[0])
	
	gbl.volume = gbl.vols[v]
	
	macros.vars['_LASTVOLUME'] = macros.vars['_VOLUME']
	macros.vars['_VOLUME'] = v

		

def adjvolume(ln):
	""" Adjust the ratio used in the volume table. """
	
	if len(ln) !=2:
		error("Use: AdjustVolume DYN RATIO.")
		
	v=ln[0].upper()
	if not v in gbl.vols:
		error("Dynamic '%s' for AdjustVolume is unknown." % ln[0] )
	
	r = stoi(ln[1], "Expecting a value for VolumeAdjust %s, not %s." %
				(ln[0], ln[1]) )
				
	if r<0:
		error("Percentage for AdjustVolume %s must be postive, not %s." %
				(ln[0], r) )
			
	if r>180:
		warning("%s is a very large AdjustVolume percentage." % r )
		
	gbl.vols[v]=r
		
	
def channelVol(ln):
	""" Set the master channel volume for all tracks."""
	
	for n in gbl.tnames:
		if gbl.tnames[n].channel:
			trackChannelVol(n, ln)

		
def cresc(ln):
	fvolume( 1, ln)


def decresc(ln):
	fvolume( -1, ln)

		
def fvolume(dir, ln):

	global futureVol
	
	if len(ln) != 2:
		error("Use: (De)Cresc Final-Dynamic Num-Bars")
		
	bcount = stoi(ln[1], "Type error in (De)Cresc, '%s'." % ln[1] )
	if bcount < 0:
		error("Bar count for (De)Cresc must be postive.")
		
	v=ln[0].upper()
	if not v in gbl.vols:
		error("Unknown volume '%s'." % ln[0] )

	
	macros.vars['_LASTVOLUME'] = macros.vars['_VOLUME']
	macros.vars['_VOLUME'] = v
	
	dest = gbl.vols[v]
	
	v=gbl.volume	
	if dir > 0 and dest <= v:
		warning("Cresc volume less than current setting. " 
			" Line %s." % gbl.lineno )
			
	if dir < 0 and dest >= v:
		warning("Decresc volume greater than current setting. " 
			" Line %s." % gbl.lineno )

	step = ( dest-gbl.volume ) / bcount

	futureVol=[]
	
	for a in range(bcount-1):
		v += step
		futureVol.append(int(v))
	futureVol.append(dest)	


#######################################
# Groove stuff

	
def grooveDefine(ln):
	""" Define a groove. 
	
	Current settings are assigned to a groove name.
	"""
	
	if not len(ln):
		error("Use: DefGroove  Name")
		
	slot=ln[0].upper()
	
	if '/' in slot:
		error("The '/' is not permitted in a groove name.")
		
	grooveDefineDo(slot)

	if gbl.debug:
		print "Groove settings saved to '%s'." % slot
	
	gbl.mkGrooveList.append(slot)
			
	if len(ln) > 1:
		MMAdocs.docDefine(ln)
		
def grooveDefineDo(slot):

	global seqRnd
	
	for n in gbl.tnames.values():
		n.saveGroove(slot)

	gbl.settingsGroove[slot] = {'SEQSIZE': gbl.seqSize,
			'QPERBAR': gbl.QperBar,
			'SEQRND':  seqRnd,
			'TIMESIG': MMAmidi.timeSig.get()  }
			

def groove(ln):
	""" Select a previously defined groove. """
	
	if len(ln) != 1:
		error("Use: Groove Name")
	
	slot=ln[0].upper()

	if not slot in gbl.settingsGroove:

		if gbl.debug:
			print "Groove '%s' not defined. Trying auto-load from libraries" \
				% slot
		
		l=loadGrooveDir(slot)	# name of the lib file with groove

		if l:
			if gbl.debug:
				print "Attempting to load groove '%s' from '%s'." \
					% (slot, l)
				
			usefile([l])

			if not slot in gbl.settingsGroove:
				error("Groove '%s' not found. Have libraries changed "
					"since last 'mma -g' run?" % slot)	
		
		else:
			error("Groove '%s' could not be found in memory "
				"or library files" % slot )

	grooveDo(slot)
	
	macros.vars['_LASTGROOVE'] = macros.vars['_GROOVE']
	macros.vars['_GROOVE']     = slot
	if macros.vars['_LASTGROOVE'] == '':
		macros.vars['_LASTGROOVE']=slot


	if gbl.debug:
		print "Groove settings restored from '%s'." % slot
	
def grooveDo(slot):
	""" This is separate from groove() so we can call it from
		usefile() with a qualified name. """
		
	global seqRnd

	# Set seqsize first so that the class restore code
	# knows what the new size is (only a problem in SOLOs)
	
	g=gbl.settingsGroove[slot]
	gbl.seqSize   = g['SEQSIZE']
	gbl.QperBar   = g['QPERBAR']
	seqRnd        = g['SEQRND'] 
	n,d           = g['TIMESIG']
	if n or d:
		MMAmidi.timeSig.set(n,d)
		
	
	for n in gbl.tnames.values():
		n.restoreGroove(slot)
	gbl.seqCount = 0

		
#######################################
# File and I/O
	
def include(ln):
	""" Include a file. """

	if gbl.inpath.beginData:
		error("INCLUDE not permitted in Begin/End block")
			
	if len(ln) != 1:
		error("Use:  Include FILE" )
	ln=ln[0]

	fn = MMAfile.locFile(ln, gbl.incPath)
	if not fn:
		error("Could not find include file '%s'." % ln)
	
	else:
		parseFile(fn)
	
	
def usefile(ln):
	""" Include a library file. """

	if gbl.inpath.beginData:
		error("USE not permitted in Begin/End block")
		
	if len(ln) != 1:
		error("Use: Use FILE" )

	ln = ln[0]
	fn = MMAfile.locFile(ln, gbl.libPath)

	if not fn:
		error("Unable to locate library file '%s'." % ln)
							
	# USE saves current state, just like defining a groove.
	# Here we use a magic number which can't be created with
	# a defgroove. Save, read, restore.
	
	slot = 9988	
	grooveDefineDo(slot)
	parseFile(fn)
	grooveDo(slot)


def mmastart(ln):
	if not ln:
		error ("Use: MMAstart FILE [file...]")

	gbl.mmaStart.extend(ln)

	if gbl.debug:
		print "MMAstart set to:",
		printList(ln)
	
def mmaend(ln):
	if not ln:
		error ("Use: MMAend FILE [file...]")

	gbl.mmaEnd.extend(ln)
	
	if gbl.debug:
		print "MMAend set to:",
		printList(ln)


def setLibPath(ln):
	""" Set the LibPath variable.  """

	if len(ln) > 1:
		error("Only one path can be entered for LibPath.")
	
	f = os.path.expanduser(ln[0])
	
	if gbl.debug:
		print "LibPath set to", f

	gbl.libPath = f

def setIncPath(ln):
	""" Set the IncPath variable.  """

	if len(ln)>1:
		error("Only one path is permitted in SetIncPath.")

	f = os.path.expanduser(ln[0])
	
	if gbl.debug:
		print "IncPath set to", f

	gbl.incPath=f
		
def setOutPath(ln):
	""" Set the Outpath variable. """
	
	if not ln:
		gbl.outPath = ""
		
	elif len(ln) > 1:
		error ("Use: SetOutPath PATH.")	
	
	else:
		gbl.outPath = os.path.expanduser(ln[0])
		

	
#######################################
# Sequence

def seqsize(ln):
	""" Set the length of sequcences. """
	
	
	if len(ln) !=1:
		error("Usage 'SeqSize N'.")
				
	n = stoi(ln[0], "Argument for SeqSize must be integer.")
					
	# Setting the sequence size always resets the seq point
			
	gbl.seqCount = 0
			
	# Now set the sequence size for each track. The class call
	# will expand/contract existing patterns to match the new
	# size.
			
	gbl.seqSize = n
	for a in gbl.tnames.values():
		a.setSeqSize()

	if gbl.debug:
		print "Set SeqSize to ", n
	
	macros.vars['_SEQSIZE']=str(n)
	

def seq(ln):
	""" Set the sequence point. """
	
	global seqRnd
	
	if len(ln) == 0:
		s = 0
	elif len(ln)==1:
		s = stoi(ln[0], "Expecting integer value after SEQ")
	else:
		error("Use: SEQ or SEQ NN to reset seq point.")
	
	
	if s > gbl.seqSize:
		error("Sequence size is '%d', you can't set to '%d'." % 
			(gbl.seqSize, s))
	
	if s==0:
		s=1
		
	if s<0:
		error("Seq parm must be greater than 0, not %s", s)
				
	gbl.seqCount = s-1
	
	seqRnd = 0
		
	

def seqClear(ln):
	""" Clear all sequences. """
	
	global futureVol
	
	if ln:
		error ("Use: 'SeqClear' with no args")
		
	for n in gbl.tnames.values():
		n.clearSequence()
	futureVol = []


def setSeqRnd(ln):
	""" Set random order for all tracks. """
	
	global seqRnd
	
	if ln:
		error("Use: SeqRnd with no paramater.")
		
	seqRnd = 1

	
def seqNoRnd(ln):
	""" Reset random order for specified track. """
	
	global seqRnd
	
	if ln:
		error("Use: SeqNoRnd")
		
	seqRnd = 0

#######################################
# Midi

def rawMidi(ln):
	""" Send hex bytes as raw midi stream. """
	
	mb=''
	for a in ln:
		a=stoi(a)
		
		if a<0 or a >0xff:
			error("All values must be in the range "
				"0 to 0xff, not '%s'" % b)
						
		mb += chr(a)
			
	gbl.mtrks[0].addToTrack(gbl.tickOffset, mb)

	if gbl.debug:
		print "Inserted raw midi in metatrack: ",
		for b in mb:
			print '%02x' % ord(b),
		print
			

def mdefine(ln):
	""" Set a midi seq pattern. """

	if not ln:
		error("MDefine needs arguments.")
	
	name = ln[0]
	if name.startswith('_'):
		error("Names with a leading underscore are reserved.")
		
	if name.upper() == 'Z':
		error("The name 'Z' is reserved.")

	MMAmdefine.mdef.set(name, ' '.join(ln[1:]))
	
	
def setMidiFileType(ln):
	""" Set some MIDI file generation flags. """

	if not ln:
		error("USE: MidiFile [SMF=0/1] [RUNNING=0/1]")

	for l in ln:
		mode, val = l.upper().split('=')

		if mode == 'SMF':
			if val == '0':				
				gbl.midiFileType = 0
			elif val == '1':
				gbl.midiFileType = 1
			else:
				error("Use: MIDIFile SMF=0/1")
				
			if gbl.debug:
				print "Midi Filetype set to", gbl.midiFileType

				
		elif mode == 'RUNNING':
			if val == '0':
				gbl.runningStatus = 0
			elif val == '1':
				gbl.runningStatus = 1
			else:
				error("Use: MIDIFile RUNNING=0/1")
		
			if gbl.debug:
				print "Midi Running Status Generation set to", 
				if gbl.runningStatus:
					print 'ON (Default)'
				else:
					print 'OFF'

				
		else:
			error("Use: MIDIFile [SMF=0/1] [RUNNING=0/1]")	
	
	
def setChPref(ln):
	""" Set MIDI Channel Preference. """
	
	if not ln:
		error("Use: ChannelPref TRACKNAME=CHANNEL [...]")
		
	for i in ln:
		if '=' not in i:
			error("Each item in ChannelPref must have an '='.")
			
		n,c = i.split('=')
		
		c = stoi(c, "Expecting an integer for ChannelPref, not '%s'." % c)
		
		if c<1 or c>16:
			error("Channel for ChannelPref must be 1..16, not %s." % c)
			
		gbl.midiChPrefs[n.upper()]=c
		
	if gbl.debug:
		print "ChannelPref:",
		for n,c in gbl.midiChPrefs.items():
			print "%s=%s" % (n,c),
		print


def setTimeSig(ln):
	""" Set the midi time signature. """
	
	if len(ln) != 2:
		error("TimeSig needs 2 args (num/dem).")
	
	nn = stoi(ln[0])
	
	if nn<1 or nn>126:
		error("Timesig NN must be 1..126")
		
	dd = stoi(ln[1])
	if   dd == 1:  dd = 0
	elif dd == 2:  dd = 1
	elif dd == 4:  dd = 2
	elif dd == 8:  dd = 3
	elif dd == 16: dd = 4
	elif dd == 32: dd = 5
	elif dd == 64: dd = 6
	else:
		error("Unknown value for timesig denominator")
	
	MMAmidi.timeSig.set(nn,dd)


	
	
#######################################
# Misc
	
	
def keySig(ln):
	""" Set the keysignature. Used by solo tracks."""
	
	if len(ln) != 1 or len(ln[0]) != 2:
		error("KeySig Usage: 2b, 3#, etc.., not '%s'" % ' '.join(ln) )
		
	c=ln[0][0]
	f=ln[0][1].upper()

	if f in ('B', '&'):
		gbl.keySig[0]='b'
	elif f == '#':
		gbl.keySig[0]='#'
	else:
		error("2nd char in KeySig must be 'b' or '#', not '%s'" % f)

	if not c in "01234567":
		error("1st char in KeySig must be digit 0..7,  not '%s'" % c)

	gbl.keySig[1] = int(c)

	n = gbl.keySig[1]
	if n and gbl.keySig[0] == 'b':
		n=256-n
		
	gbl.mtrks[0].addKeySig(gbl.tickOffset, n)
	
	if gbl.debug:
		if f == '#':
			f="Sharps"
		else:
			 f == "Flats"
		
		print "KeySig set to %s	%s" % (c, f)
		

def transpose(ln):
	""" Set transpose value. """
	

	if len(ln) != 1:
		error("Use: Transpose N.")
	
	t = stoi(ln[0], "Argument for Tranpose must be an integer, "
		"not '%s'" % ln[0])
	if t < -12 or t > 12:
			error("Tranpose %s out-of-range; must be -12..12." % t)

	gbl.transpose = t

	macros.vars['_TRANSPOSE']=str(t)
	
	if gbl.debug:
		print "Set Transpose to %s" % t





def lnPrint(ln):
	print " ".join(ln)
	
	
def printActive(ln):
	""" Print a list of the active tracks. """
	
	print "Active tracks, groove:", macros.vars['_GROOVE'], ' '.join(ln)

	l = gbl.tnames.keys()
	l.sort()
	for a in l:
		f=gbl.tnames[a]
		if f.sequence:
			print "  ",a
	print
	
	
def setDebug(ln):
	""" Set debugging options dynamically. """
	
	msg=( "Use: Debug MODE=On/Off where MODE is one or more of "
			"DEBUG, FILENAMES, PATTERNS, SEQUENCE, "
			"RUNTIME, WARNINGS or EXPAND." )
		
	
	if not len(ln):
		error(msg)

	setDebugMacro('_LASTDEBUG')
	
	for l in ln:
		try:
			mode, val = l.upper().split('=')
		except:
			error("Each debug option must contain a '=', not '%s'" % l)
		
		if val == 'ON' or val == '1':
			setting = 1
		elif val == 'OFF' or val == '0':
			setting = 0
		else:
			error(msg)
			
		if mode == 'DEBUG':
			gbl.debug = setting
			if gbl.debug:
				print "Debug=%s." % val
			
		elif mode == 'FILENAMES':
			gbl.showFilenames = setting
			if gbl.debug:
				print "ShowFilenames=%s." % val

		elif mode == 'PATTERNS':
			gbl.pshow = setting
			if gbl.debug:
				print "Pattern display=%s." % val
			
		elif mode == 'SEQUENCE':
			gbl.seqshow = setting
			if gbl.debug:
				print "Sequence display=%s." % val
							
		elif mode == 'RUNTIME':
			gbl.showrun = setting
			if gbl.debug:
				print "Runtime display=%s." % val
			
		elif mode == 'WARNINGS':
			gbl.noWarn = not(setting)
			if gbl.debug:
				print "Warning display=%s." % val
			
		elif mode == 'EXPAND':
			gbl.showExpand = setting
			if gbl.debug:
				print "Expand display=%s." % val
	
		else:
			error(msg)

	setDebugMacro('_DEBUG')
	
###########################################################
###########################################################
## Track specific commands


#######################################
# Pattern/Groove
		
def trackDefPattern(name, ln):
	""" Define a pattern for a track. 
	"""
	
	""" Use the type-name for all defines.... check the track 
		names and if it has a '-' in it, we use only the
		part BEFORE the '-'. So DRUM-Snare becomes DRUM.
	"""

	ln=ln[:]
	
	name=name.split('-')[0]
	
	trackAlloc(name, 1)
	
	if ln:
		pattern = ln.pop(0).upper()
	else:
		error("Define is expecting a pattern name.")

	if pattern in ('z', 'Z', '-'):
		error("Pattern name '%s' is reserved." % pattern)
		
	if pattern.startswith('_'):
		error("Names with a leading underscore are reserved.")

	if not ln:
		error("No pattern list given for '%s %s'." % (name, pattern) )
				
	ln=' '.join(ln)
	gbl.tnames[name].definePattern(pattern, ln)


def trackSequence(name, ln):
	""" Define a sequence for a track.
	
		The format for a sequence:
			TrackName Seq1 [Seq2 ... ]
			
			Note, that SeqX can be a predefined seq or { seqdef }
			 The {} is dynamically interpreted into a def.
    """
	
	if not ln:
		error ("Use: %s Sequence NAME [...]" % name)
	
	ln = ' '.join(ln)

	""" Extract out any {} definitions and assign them to new
		define variables (__1, __99, etc) and melt them
		back into the string.
	"""

	ids=1
	while 1:
		sp = ln.find("{")

		if sp<0:
			break

		ln, s = pextract(ln, "{", "}", 1)
		if not s:
			error("Did not find matching '}' for '{'")

		pn = "_%s" % ids
		ids+=1

		trk=name.split('-')[0]
		trackAlloc(trk, 1)

		gbl.tnames[trk].definePattern(pn, s[0])
		ln = ln[:sp] + ' ' + pn + ' ' + ln[sp:]

	ln=ln.split()

	gbl.tnames[name].setSequence(ln)


def trackSeqClear(name,  ln):
	""" Clear sequence for specified tracks.
	
	Note: "Drum SeqClear" clears all Drum tracks,
		"Drum3 SeqClear" clears track Drum3.
	"""
	
	for n in gbl.tnames:
		if n.find(name) == 0:
			gbl.tnames[n].clearSequence()
	

def trackSeqRnd(name, ln):
	""" Set random order for specified track. """
	
	if ln:
		error("Use: %s SeqRnd with no paramater." % name)
		
	gbl.tnames[name].setRnd()


def trackSeqNoRnd(name, ln):
	""" Reset random order for specified track. """

	if ln:
		error("Use: %s SeqNoRnd with no paramater." % name)
		
	gbl.tnames[name].setNoRnd()


def trackGroove(name, ln):
	""" Select a previously defined groove for a single track. """
	
	if len(ln) != 1:
		error("Use: %s Groove Name" % name)


	slot = ln[0].upper()
	
	if not slot in gbl.settingsGroove:
		error("Groove '%s' not defined" % slot)
	
	g=gbl.tnames[name]
	g.restoreGroove(slot)
	g.setSeqSize()
	
	if gbl.debug:
		print "%s Groove settings restored from '%s'." % (name, slot)
	
	
def trackRiff(name, ln):
	""" Set a riff for a track.
	
		A riff is just a temporary pattern for the current bar.
	"""
	
	ln=' '.join(ln)
	
	v = gbl.tnames[name].vtype
	if v != 'SOLO' and v != 'MELODY':
		ln = ln.rstrip('; ')
		
	gbl.tnames[name].setRiff(ln)

def trackMultiRiff(name, ln):
	""" Set a multi-riff for a track.
	
		Same as trackRiff but this function stacks riffs.
	"""
	
	ln=' '.join(ln)
	
	v = gbl.tnames[name].vtype
	if v != 'SOLO' and v != 'MELODY':
		ln = ln.rstrip('; ')
		
	gbl.tnames[name].setMultiRiff(ln)


def deleteTrks(ln):
	""" Delete a track and free the MIDI track. """
	
	if not len(ln):
		error("Use Delete Track [...]")
		
	for name in ln:
		name=name.upper()
		if name in gbl.tnames:
			tr = gbl.tnames[name]
		else:
			error("Track '%s' does not exist" % name)

		if tr.channel:
			tr.doMidiClear()
			tr.clearPending()
			
			if tr.riff:
				warning("%s has pending RIFF(s)" % name)			
			gbl.midiAvail[tr.channel] -= 1

			# NOTE: Don't try deleting 'tr' since it's just a copy!!
	
			del gbl.tnames[name]
		
		if not gbl.deletedTracks.count(name):
			gbl.deletedTracks.append(name)
			
		if gbl.debug:
			print "Track '%s' deleted" % name
		
	

#######################################
# Volume

def trackRvolume(name, ln):
	""" Set random volume for specific track. """
	
	if not ln:
		error ("Use: %s RVolume N [...]." % name)

	gbl.tnames[name].setRVolume(ln)
	
def trackCresc(name, ln):
	error("(De)Crescendo only supported in master context.")
	
			
def trackVolume(name, ln):
	""" Set volume for specific track. """

	if not ln:
		error ("Use: %s Volume DYN [...]." % name)
		
	gbl.tnames[name].setVolume(ln)


def trackChannelVol(name, ln):
	""" Set the channel volume for a track."""
	
	if len(ln) != 1:
		error("Use: %s ChannelVolume." % name)
	
	v=stoi(ln[0], "Expecting integer arg, not %s." % ln[0])	
		
	if v<0 or v>127:
		error("ChannelVolume must be 0..127")
		
	gbl.tnames[name].setChannelVolume(v)


def trackAccent(name, ln):
	""" Set emphasis beats for track."""
	
	gbl.tnames[name].setAccent(ln)
	
								
#######################################
# Timing

def trackCut(name, ln):
	""" Insert a ALL NOTES OFF at the given offset. """


	global barNum
		
	if not len(ln):
		ln=['0']
		
	if  len(ln) != 1:
		error("Use: %s Cut Offset" % name)
		
		
	offset = stof(ln[0], "Cut offset expecting value, (not '%s')." % ln[0])
	
	if offset < -gbl.QperBar or offset > gbl.QperBar:
		warning("Cut: %s is a large beat offset." % offset)


	
	moff = int(gbl.tickOffset + (gbl.BperQ * offset))
	
	if moff < 0:
		error("Calculated offset for Cut comes before start of track.")
	
	""" Insert allnoteoff directly in track. This skips the normal
		queueing in pats because it would never take if at the end
		of a track.
	"""
		
	m = gbl.tnames[name].channel
	if m and len(gbl.mtrks[m].miditrk) > 1:
		gbl.mtrks[m].addNoteOff(moff)


		if gbl.debug:
			print "%s Cut: Beat %s, Bar %s" % (name, offset, barNum + 1)


def trackMallet(name, ln):
	""" Set repeating-mallet options for solo/melody track. """
	
	if not ln:
		error("Use: %s Mallet <Option=Value> [...]." % name)
		
	gbl.tnames[name].setMallet(ln)

	
def trackRtime(name, ln):
	""" Set random timing for specific track. """
	
	if not ln:
		error ("Use: %s RTime N [...]." % name)
	
	gbl.tnames[name].setRTime(ln)


def trackRskip(name, ln):
	""" Set random skip for specific track. """
	
	if not ln:
		error ("Use: %s RSkip N [...]." % name)

	gbl.tnames[name].setRSkip(ln)

			
def trackArtic(name, ln):
	""" Set articulation. """
	
	if not ln:
		error("Use: %s Articulation N [...]." % name)
			
	gbl.tnames[name].setArtic(ln)

#######################################
# Chord stuff
	
def trackCompress(name, ln):
	""" Set (unset) compress for track. """
	
	if not ln:
		error("Use: %s Compress <value[s]>" % name)
		
	gbl.tnames[name].setCompress(ln)
	
	
def trackVoicing(name, ln):
	""" Set Voicing options. Only valid for chord tracks at this time."""
	
	if not ln:
		error("Use: %s Voicing <MODE=VALUE> [...]" % name)
		
	gbl.tnames[name].setVoicing(ln)
	

def trackDuplicate(name, ln):
	""" Set (unset) octave duplication for track. """
	
	if not ln:
		error("Use: %s Duplicate <value> ..." % name)
		
	gbl.tnames[name].setDuplicate(ln)


def trackDupRoot(name, ln):
	""" Set (unset) the root note duplication. Only applies to chord tracks. """
	
	if not ln:
		error("Use: %s DupRoot <value> ..." % name)
		
	gbl.tnames[name].setDupRoot(ln)


def trackChordLimit(name, ln):
	""" Set (unset) ChordLimit for track. """
	
	if len(ln) != 1:
		error("Use: %s ChordLimit <value>" % name)
		
	gbl.tnames[name].setChordLimit(ln[0])

def trackRange(name, ln):
	""" Set (unset) Range for track. Only effects arp and scale. """
	
	if not ln:
		error("Use: %s Range <value> ... " % name)
		
	gbl.tnames[name].setRange(ln)


def trackInvert(name, ln):
	""" Set invert for track."""
	
	if not ln:
		error("Use: %s Invert N [...]." % name)
	
	gbl.tnames[name].setInvert(ln)
				

		
def trackOctave(name, ln):
	""" Set octave for specific track. """
	
	if not ln:
		error ("Use: %s Octave N [...], (n=0..10)" % name)
	
	gbl.tnames[name].setOctave( ln )


def trackStrum(name, ln):
	""" Set all specified track strum. """
	
	if not ln:
		error ("Use: %s Strum N [...]" % name)
		
	gbl.tnames[name].setStrum( ln )


def trackHarmony(name, ln):
	""" Set harmony value. """
	
	if not ln:
		error("Use: %s Harmony N [...]" % name)
		
	gbl.tnames[name].setHarmony(ln)
	
def trackHarmonyOnly(name, ln):
	""" Set harmony only for track. """
	
	if not ln:
		error("Use: %s HarmonyOnly N [...]" % name)
		
	gbl.tnames[name].setHarmonyOnly(ln)


#######################################
# MIDI setting

	
def trackChannel(name, ln):
	""" Set the midi channel for a track."""
	
	if not ln:
		error("Use: %s Channel" % name)
		
	gbl.tnames[name].setChannel(ln[0])


def trackMdefine(name, ln):
	""" Set a midi seq pattern. Ignore track name."""
	
	mdefine(ln)


def trackMidiExt(ln):	
	""" Helper for trackMidiSeq() and trackMidiVoice()."""
	
	ids=1
	while 1:
		sp = ln.find("{")

		if sp<0:
			break

		ln, s = pextract(ln, "{", "}", 1)
		if not s:
			error("Did not find matching '}' for '{'")

		pn = "_%s" % ids
		ids+=1

		MMAmdefine.mdef.set(pn, s[0])
		ln = ln[:sp] + ' ' + pn + ' ' + ln[sp:]
		
	return ln.split()

def trackMidiClear(name, ln):
	""" Set MIDI command to send at end of groove. """
	
	if not ln:
		error("Use %s MIDIClear Controller Data" % name)
	
	
	if len(ln) == 1 and ln[0] == '-':
		gbl.tnames[name].setMidiClear( '-' )
	else:
		ln=' '.join(ln)
		if ln.count('{') or ln.count('{'):
			error("{}s are not permitted in %s MIDIClear command." % name)
		gbl.tnames[name].setMidiClear( trackMidiExt( '{' + ln + '}' ))

	
def trackMidiSeq(name, ln):
	""" Set reoccurring MIDI command for track. """
	
	if not ln:
		error("Use %s MidiSeq Controller Data " % name)
		
	if len(ln) == 1 and ln[0]== '-':
		gbl.tnames[name].setMidiSeq('-')
	else:
		gbl.tnames[name].setMidiSeq( trackMidiExt(' '.join(ln) ))


def trackMidiVoice(name, ln):
	""" Set single shot MIDI command for track. """
	
	if not ln:
		error("Use %s MidiVoice Controller Data" % name)

	if len(ln) == 1 and ln[0] == '-':
		gbl.tnames[name].setMidiVoice( '-' )
	else:
		gbl.tnames[name].setMidiVoice( trackMidiExt(' '.join(ln) ))
	

def trackChShare(name, ln):
	""" Set MIDI channel sharing."""
	
	if len(ln) !=1:
		error("Use: %s ChShare TrackName" % name)
	
	gbl.tnames[name].setChShare(ln[0])
			
				
def trackVoice(name, ln):
	""" Set voice for specific track. """
	
	if not ln:
		error ("Use: %s Voice NN [...]" % name)

	gbl.tnames[name].setVoice(ln)


def trackPan(name, ln):
	""" Set the Midi Pan value for a track."""
	
	if len(ln) != 1:
		error("Use: %s PAN NN" % name)
		
	gbl.tnames[name].setPan(ln[0])
	

def trackOff(name, ln):
	""" Turn a track off """
	
	if ln:
		error("Use: %s OFF with no paramater." % name)

	gbl.tnames[name].setOff()


def trackOn(name, ln):
	""" Turn a track on """
	
	if ln:
		error("Use: %s ON with no paramater." % name)

	gbl.tnames[name].setOn()


def trackTone(name, ln):
	""" Set the tone (note). Only valid in drum tracks."""
	
	if not ln:
		error("Use: %s Tone N [...]." % name)
	
		
	gbl.tnames[name].setTone(ln)	


def trackGlis(name, ln):
	""" Enable/disable portamento. """
	
	if len(ln) != 1:
		error("Use: %s Portamento NN, off=0, 1..127==on." % name)
		
	gbl.tnames[name].setGlis(ln[0])


#######################################
# Misc

def trackDrumType(name, ln):
	""" Set a melody or solo track to be a drum solo track."""
	
	tr = gbl.tnames[name]
	if tr.vtype not in ('SOLO', 'MELODY'):
		error ("Only Solo and Melody tracks can be to DrumType, not '%s'."
			% name)
	if ln:
		error("No parmeters permitted for DrumType command.")
	
	tr.setDrumType()
	
	
def trackDirection(name, ln):
	""" Set scale/arp direction. """
	
	if not ln:
		error("Use: %s Direction OPT" % name)
		
	gbl.tnames[name].setDirection(ln)

	
def trackScaletype(name, ln):
	""" Set the scale type. """

	if not ln:
		error("Use: %s ScaleType OPT" % name)

	gbl.tnames[name].setScaletype(ln)


def trackCopy(name, ln):
	""" Copy setting in 'ln' to 'name'. """
	
	if len(ln) != 1:
		error("Use: %s Copy ExistingTrack" % name)
	
	gbl.tnames[name].copySettings(ln[0].upper())
	
	
def trackUnify(name, ln):
	""" Set UNIFY for track."""
	
	if not len(ln):
		error("Use %s UNIFY 1 [...]" % name)
		
	gbl.tnames[name].setUnify(ln)
	
######################################################
######################################################
### Process a bar of music

def mdata(ln):
	""" Process a line of music data. """
	
	"""	Expand bar line data.
	
		1. A data line can have an option bar number at the start
		of the line. Makes debugging input easier. The next
		block strips leading integers off the line.
		Note that a line number on a line by itself it okay.
		
		2. Extract optional lyric info. This is anything in []s.

		3. Extract solo line. This is anything in {}s.
				
		4. Process optional repeat counts.
		
		5. Expand line to correct number of beats. This is done
		by adding '/'s to the line until it is the correct length.
		
		6. Convert all '/'s in the line to chord names.
	"""

	global lastChord, barNum, seqRnd, futureVol

	
	ln = ln[:]
	try:
		int(ln[0])		# strip off leading line number
		ln.pop(0)
		if not ln:		# ignore empty lines
			return 
	except:
		pass
	
	# Grab optional repeat count at end of bar
	
	if len(ln)>1 and ln[-2]=='*':
		rptcount = stoi(ln.pop(), "Expecting integer after '*'")
		ln.pop()	# pull off the '*'
	else:
		rptcount = 1
	
	ln = ' '.join(ln)

	# Set lyrics from [stuff] in the current line or 
	# stuff previously stored with LYRICS SET.
	
	ln, lyrics = lyric.extract(ln, barNum, rptcount)
	
	# Same for solo: {stuff} or RIFF(S). The solo variable is not used.
	
	ln, solo = MMApatSolo.extractSolo(ln, rptcount)
	
	# Pad out chords to correct number of '/'s
	
	ln=ln.split()

	if not ln:
		error("Expecting music (chord) data. Even lines with\n"
			"  lyrics or solos still need a chord.")
				
	i=gbl.QperBar - len(ln)
	if i<0:
		error("Too many chords in line. Max is %s, not %s." % 
			(gbl.QperBar, len(ln) ) )
	if i:
		ln.extend( ['/'] * i )


	""" We now have a valid line. It'll look something like:
	
			['Cm', '/', 'z', 'F#']
		
		For each bar we create a ctable structure. This is just
		a list of CTables, one for each beat division.
		Each entry has the offset (in midi ticks), chordname, etc.
		
		Special processing in needed for 'z' options in chords. A 'z' can
		be of the form 'CHORDzX', 'z!' or just 'z'. 
	"""
	
	beat = 0
	ctable=[]

	for c in ln:
		if c == '/':
			c=lastChord
			if not lastChord:
				error("A chord has to be set before you can use a '/'.")
		else:
			lastChord = c

		tt=CTable()

		if 'z' in c:			# z chords.
			c, r = c.split('z', 1)	# chord name/track mute
			if not c:
			
				if  r=='!':     # mute all for 'z!'
					r='DCAWBS'	
					c='z'	    # dummy chord name

				elif not r:     # mute all tracks except Drum 'z'
					r='CBAWS'
					c='z'
				
				# illegal contruct -- 'zDS'
			
				else:
					error("To mute individual tracks you must " 
						"use a chord/z combination not '%s'." % ln)
			
			else:

				# illegal construct -- 'Cz!'
			
				if r=='!':
					error("'%sz!' is illegal. 'z!'  mutes all tracks "
						"so you can't include the chord." % c)
				
				elif not r:
					error("'%sz' is illegal. You must specify tracks "
						"if you use a chord." % c )

			for v in r:
				if v == 'C':
					tt.chordZ = 1
				elif v == 'B':
					tt.bassZ = 1
				elif v == 'A':
					tt.arpeggioZ = 1
				elif v == 'W':
					tt.walkZ = 1
				elif v == 'D':
					tt.drumZ = 1
				elif v == 'S':
					tt.scaleZ = 1

				else:
					error("Unknown voice '%s' for rest in '%s'." % (v,r))


		tt.offset = beat * gbl.BperQ
		tt.chord = ChordNotes(c)

		ctable.append(tt)
		beat += 1

	# Create MIDI data for the bar

	for rpt in range(rptcount):
		if futureVol:
			gbl.volume = futureVol.pop(0)

		if seqRnd:
			gbl.seqCount = random.randrange(gbl.seqSize)
			
		""" Special loop for solo/harmony tracks... We take the
			first track in autosolotracks[] and if it's assigned
			and has data we duplicate the data to any other solo/melody
			tracks in the list which are set as harmonyonly.
		"""
		
		MMApatSolo.copySoloToHarmony()


		""" Process each track. It is important that the track classes
			are written so that the ctable passed to them IS NOT MODIFIED.
			This applies especially to chords. If the track class changes
			the chord, then restore it before returning!!!
		"""
		
		for a in gbl.tnames.values():
			a.bar(ctable)
		
		# Adjust counters
		
		barNum += 1
		
		if barNum > gbl.maxBars:
			error("Capacity exceeded. Maxbar setting is %s. Use -m option."
				% gbl.maxBars)
				
		gbl.tickOffset += (gbl.QperBar * gbl.BperQ)
			
		gbl.seqCount = (gbl.seqCount+1) % gbl.seqSize

		# Enabled with the -r command line option
		
		if gbl.showrun:
			print "%3d:" % barNum,
			for c in ln:
				print c,
			if lyrics:
				print lyrics,
			print
		
""" =================================================================

	Command jump tables. These need to be at then end of this module
	to avoid undefined name errors. The tables are only used in
	the parse() function.

	The first table is for the simple commands ... those which DO NOT
	have a leading trackname. The second table is for commands which
	require a leading track name when called in mma file.
	
	The function lists are in alpha-order. 
"""

simpleFuncs={	
	'ADJUSTVOLUME':        adjvolume,
	'AUTHOR':              MMAdocs.docAuthor,
	'AUTOSOLOTRACKS':      MMApatSolo.setAutoSolo,
	'BEATADJUST':          beatAdjust,
	'CHANNELPREF':         setChPref,
	'CHANNELVOLUME':       channelVol,
	'COMMENT':             comment,
	'CRESC':               cresc,
	'CUT':                 cut,
	'DEBUG':               setDebug,
	'DEC':                 macros.vardec,
	'DECRESC':             decresc,
	'DEFGROOVE':           grooveDefine,
	'DELETE':              deleteTrks,
	'DOC':                 MMAdocs.docNote,
	'ELSE':                ifelse,
	'ENDIF':               ifend,
	'ENDMSET':             endmset,
	'ENDREPEAT':           repeatend,
	'EOF':                 eof,
	'FERMATA':             fermata,
	'GOTO':                goto,
	'GROOVE':              groove,
	'IF':                  macros.varIF, 
	'IFEND':               ifend,
	'INC':                 macros.varinc,
	'INCLUDE':             include,
	'KEYSIG':              keySig,
	'LYRIC':               lyric.option,
	'MIDIDEF':             mdefine,
	'MIDI':                rawMidi,
	'MIDIFILE':            setMidiFileType,
	'MIDIINC':             MMAmidiIn.midiinc,
	'MMAEND':              mmaend,
	'MMASTART':            mmastart,
	'MSET':                macros.msetvar,
	'MSETEND':             endmset,
	'PRINT':               lnPrint,
	'PRINTACTIVE':         printActive,
	'REPEAT':              repeat,
	'REPEATEND':           repeatend,
	'REPEATENDING':        repeatending,
	'RTIME':               rtime,
	'RSKIP':               rskip,
	'RVOLUME':             rvolume,
	'SEQ':                 seq,
	'SEQCLEAR':            seqClear,
	'SEQNORND':            seqNoRnd,
	'SEQRND':              setSeqRnd,
	'SEQSIZE':             seqsize,
	'SET':                 macros.setvar,
	'SETINCPATH':          setIncPath,
	'SETLIBPATH':          setLibPath,
	'SETOUTPATH':          setOutPath,
	'SHOWVARS':            macros.showvars,
	'TEMPO':               tempo,
	'TIME':                setTime,
	'TIMESIG':             setTimeSig,
	'UNSET':               macros.unsetvar,
	'USE':                 usefile,
	'VEXPAND':             macros.vexpand,
	'VOICETR':             MMAtranslate.vtable.set,
	'VOLUME':              volume,
	'TRANSPOSE':           transpose
  }


trackFuncs={	
	'ARTICULATE':          trackArtic,
	'CHANNEL':             trackChannel,
	'CHANNELVOLUME':       trackChannelVol,
	'CHSHARE':             trackChShare,
	'COMPRESS':            trackCompress,
	'COPY':                trackCopy,
	'CRESC':               trackCresc,
	'CUT':                 trackCut,
	'DECRESC':             trackCresc,
	'DIRECTION':           trackDirection,
	'DRUMTYPE':            trackDrumType,
	'DUPLICATE':           trackDuplicate,
	'DUPROOT':             trackDupRoot,
	'ACCENT':              trackAccent,
	'GROOVE':              trackGroove,
	'HARMONY':             trackHarmony,
	'HARMONYONLY':         trackHarmonyOnly,
	'INVERT':              trackInvert,
	'LIMIT':               trackChordLimit,
	'MALLET':              trackMallet,
	'MIDIDEF':             trackMdefine,
	'MIDICLEAR':           trackMidiClear,
	'MIDISEQ':             trackMidiSeq,
	'MIDIVOICE':           trackMidiVoice,
	'OCTAVE':              trackOctave,
	'OFF':                 trackOff,
	'ON':                  trackOn,
	'PAN':                 trackPan,
	'PORTAMENTO':          trackGlis,
	'RANGE':               trackRange,
	'RIFF':                trackRiff,
	'RIFFS':               trackMultiRiff,
	'RSKIP':               trackRskip,
	'RTIME':               trackRtime,
	'RVOLUME':             trackRvolume,
	'SCALETYPE':           trackScaletype,
	'SEQCLEAR':            trackSeqClear,
	'SEQNORND':            trackSeqNoRnd,
	'SEQRND':              trackSeqRnd,
	'SEQUENCE':            trackSequence,
	'STRUM':               trackStrum,
	'TONE':                trackTone,
	'UNIFY':               trackUnify,
	'VOICE':               trackVoice,
	'VOICING':             trackVoicing,
	'VOLUME':              trackVolume,
	'DEFINE':              trackDefPattern
  } 


