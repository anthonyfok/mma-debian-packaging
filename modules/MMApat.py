
# MMApat.py

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
	

import copy, random

import MMAglobals;  gbl = MMAglobals
from MMAcommon import *
import MMAtranslate
import MMAmidi, MMAalloc, MMAmdefine

class Voicing:
	def __init__(self):
		self.mode    = None
		self.range   = 12
		self.center  = 4
		self.random  = 0
		self.percent = 0
		self.bcount  = 0
		self.dir     = 0


def seqBump(l):
	""" Expand/contract an existing sequence list to the current seqSize."""
	
	while len(l) < gbl.seqSize:
		l += l
	return l[:gbl.seqSize]

pats = {}		# Storage for all pattern defines


class PC:
	""" Pattern class.
	
		Define classes for processing drum, chord, arp, and chord track.
		These are mostly the same, so we create a base class and derive
		the others from it.
	
		We have a class for each track type. They are all derived
		from the base 'Pats' class. These classes do special processing
		like parsing a pattern tuple and creating a chord.
		
		No functions ever link to the code in this module, it is
		only included into the real track class modules.

	"""
	
	def __init__(self, nm):

		self.inited = 0		
		self.name = nm	
		self.channel = 0
		self.grooves = {}
		self.saveVols = {}
		self.ssvoice = -1	 # Track the voice set for the track
		self.smidiVoice = () # Track MIDIVoice cmds to avoid dups
		self.midiSent = 0    # if set, MIDICLEAR invoked.
				
		self.artic = (90,)	# Note length clip adjustment

		# Midi commands like Pan, Glis, etc. are stacked until musical
		# data is actually written to the track. Each item in
		# the midiPending list is a name (PAN, GLIS, etc), timeoffset, value.

		self.midiPending = []		

		self.riff = []
				
		self.disable = 0
		
		if self.vtype == 'DRUM':
			self.setChannel('10')
			if not gbl.mtrks[self.channel].trackname:
				gbl.mtrks[self.channel].addTrkName(0, 'Drum')

		self.clearSequence()		
					
		self.inited = 1
		
	##########################################
	## These are called from process() to set options

	def setCompress(self, ln):
		""" set/unset the compress flag. """


		ln=self.lnExpand(ln, 'Compress')

		vwarn = 0
		tmp=[]

		for n in ln:
			
			n = stoi(n, "Argument for %s Compress must be a value." \
					% self.name)
					
			if n < 0 or n > 5:
				error("Compress %s out-of-range; must be 0 to 5." % n)
			
				
			if n and self.vtype=='CHORD' and self.voicing.mode:
				vwarn = 1
						
			tmp.append(n)

		if vwarn:
			warning("Setting both Voicing Mode "
				"and Compress is not a good idea")			
		
		self.compress = seqBump(tmp)
		
		if self.vtype not in ("CHORD", "ARPEGGIO"):
			warning ("Compress is ignored in %s tracks." % self.vtype)
			
		if gbl.debug:
			print "Set %s Compress to " % self.name,
			printList(ln)
		
		
	def setRange(self, ln):
		""" set range. """
	
		ln=self.lnExpand(ln, 'Range')

		tmp=[]
		for n in ln:
			
			n = stoi(n, "Argument for %s Range must be a value." \
					% self.name)
					
			if n < 1 or n > 5:
				error("Range %s out-of-range; must be 1 to 5." % n)
						
			tmp.append(n)

		self.chordRange = seqBump(tmp)
		
		if self.vtype not in ("SCALE", "ARPEGGIO"):
			warning ("Range has no effect in '%s' tracks." % self.vtype)
			
		if gbl.debug:
			print "Set %s Range to " % self.name,
			printList(ln)
		
	
	def setVoicing(self, ln):
		""" set the Voicing Mode options. """
	
	
		if self.vtype != "CHORD":
			error("Voicing is not supported for %s tracks." % self.vtype)
			
		for l in ln:
			try:
				mode, val = l.upper().split('=')
			except:
				error("Each Voicing option must contain a '=', not '%s'" % l)


			if mode == 'MODE':
				valid= ("-", "OPTIMAL", "NONE", "ROOT", "COMPRESSED", "INVERT")
		
				if not val in  valid:
					error("Valid Voicing Modes are: %s" % " ".join(valid))
				
				if val in ('-', 'NONE',"ROOT"):
					val = None
		

				if val and (max(self.invert) + max(self.compress)):
					warning("Setting both VoicingMode and Invert/Compress "
						"is not a good idea")	
			
				# When we set voicing mode we always reset this. This forces
				# the voicingmode code to restart its rotations.

				self.lastChord = []	  

				self.voicing.mode = val


			elif mode == 'RANGE':
				val = stoi(val, "Argument for %s Voicing Range "
					"must be a value." % self.name)
					
				if val < 1 or val > 30:
					error("Voicing Range '%s' out-of-range; "
						"must be 1 to 30." % val)
						
				self.voicing.range = val


			elif mode == 'CENTER':
				val = stoi(val, "Argument for %s Voicing Center "
					"must be a value." % self.name)
					
				if val < 1 or val > 12:
					error("Voicing Center %s out-of-range; "
						"must be 1 to 12." % val)
									
				self.voicing.center = val
						
			elif mode == 'RMOVE':
				val = stoi(val, "Argument for %s Voicing Random "
					"must be a value." % self.name)
					
				if val <= 0 or val > 100:
					error("Voicing Random value must be 1 to 100 "
						"not %s" % val)

				self.voicing.random = val
				self.voicing.bcount = 0
					
			elif mode == 'MOVE':
				val = stoi(val, "Argument for %s Voicing Move "
					"must be a value." % self.name)
				
				if val < 0 :
					error("Voicing Move (bar count) must >= 0, not %s" % val)
				if val > 20:
					warning("Voicing Move (bar count) %s is quite large" % val)
				
				self.voicing.bcount = val			
				self.voicing.random = 0

			elif mode == 'DIR':
				val = stoi(val, "Argument for %s Voicing Dir (move direction) "
					"must be a value." % self.name)

				if not val in (1,-1):
					error("Voicing Move Dir -1, or 1, not %s" % val)
					
				self.voicing.dir = val
	
		
		
			
		if gbl.debug:
			v=self.voicing
			print "Set %s Voicing MODE=%s" % (self.name, v.mode),
			print "RANGE=%s CENTER=%s" % (v.range, v.center),
			print "RMOVE=%s MOVE=%s DIR=%s" % (v.random, v.bcount, v.dir)
			

	def setDuplicate(self, ln):
		""" set/unset octave duplication. """

		ln=self.lnExpand(ln, 'Duplicate')

		tmp = []
		for n in ln:
			n = stoi(n, "Argument for %s Duplicate must be a value." \
					% self.name)
					
			if n < -9 or n > 9:
				error("Duplicate %s out-of-range; must be -9 to 9." % n)
						
			tmp.append( n * 12)
			
		self.duplicate = seqBump( tmp )
		
		if gbl.debug:
			print "Set %s Duplicate to " % self.name,
			printList(ln)


	def setDupRoot(self, ln):
		""" set/unset root duplication. """

		ln=self.lnExpand(ln, 'DupRoot')
		
		if self.vtype != 'CHORD':
			error("RootDup can only be applied to CHORD tracks.")
		tmp = []
		
		for n in ln:
			n = stoi(n, "Argument for %s DupRoot must be a value." \
					% self.name)
					
			if n < -9 or n > 9:
				error("DupRoot %s out-of-range; must be -9 to 9." % n)
						
			tmp.append( n * 12 )
			
		self.dupRoot = seqBump( tmp )
		
		if gbl.debug:
			print "Set %s DupRoot to " % self.name,
			printList(ln)

	
	def setChordLimit(self, ln):
		""" set/unset the chordLimit flag. """
	
		n = stoi(ln, "Argument for %s ChordLimit must be a value." \
					% self.name)
					
		if n < 0 or n > 8:
			error("ChordLimit %s out-of-range; must be 0 to 8." % n)
						
		self.chordLimit = n
		
		if self.vtype not in ("CHORD", "ARPEGGIO"):
			warning ("Limit is ignored in %s tracks." % self.vtype)
			

		if gbl.debug:
			print "Set %s ChordLimit to %s" % (self.name, n)

		
	def setChannel(self, ln=None):
		""" Set the midi-channel number for a track. 
		
			 - Checks for channel duplication
			 - Auto assigns channel number if ln==''

		"""

		""" If no track number was passed, then we try to
			auto-alloc a track. First, we see if a preference
			was set via MidiChPref. If these is no preference,
			or if the preferred channel is already allocated
			we go though the list, top to bottom, to find
			an available channel.
		"""
		
		if not ln:
		
			try:
				c=gbl.midiChPrefs[self.name]
			except:
				c=0

			if not c or gbl.midiAvail[c]:
				c=0
				for a in range(16, 0, -1):
					if a!=10 and not gbl.midiAvail[a]:
						c=a
						break

			if not c:
				error("No MIDI channel is available for %s.\n"
					"Try CHShare or Delete unused tracks." % self.name)

		else:
			c = stoi(ln, "%s Channel assignment expecting Value, not %s" %
				(self.name, ln))

			if c<0 or c>16:
				error("%s Channel must be 0..16, not %s" % (self.name, ln))
			
		if c == 10:
			if self.vtype == 'DRUM':
				pass
			elif self.vtype in ('SOLO', 'MELODY') and self.drumType:
				pass
			else:
				error("Channel 10 is reserved for DRUM, not %s." % self.name)
		
		if self.vtype == 'DRUM' and c != 10:
			error("DRUM tracks must be assigned to channel 10.")
			
		# Disable the channel.

		if c == 0:
			if gbl.midiAvail[self.channel]:
				gbl.midiAvail[self.channel] -= 1
			s="%s channel disabled." % self.name
			if gbl.midiAvail[self.channel]:
				s+=" Other tracks are still using channel %s." % self.channel
			else:
				s+=" Channel %s available." % self.channel
			warning(s)
			self.channel = 0
			self.disable = 1
			return
			
			
		if c != 10:
			for a, tr in gbl.tnames.items():
				if a == self.name:	# okay to reassign same number
					continue
				
				if tr.channel == c:
					error("Channel %s is assigned to %s." % (c, tr.name ) )

		self.channel = c
		if gbl.midiAssigns[c].count(self.name) == 0:
			gbl.midiAssigns[c].append(self.name)

		gbl.midiAvail[c]+=1
		
		if not c in gbl.mtrks:
			gbl.mtrks[c]=MMAmidi.Mtrk(c)
			offset=0
			if gbl.debug:
				print "MIDI channel %s buffer created." % c
		else:
			offset = gbl.tickOffset	
			
		if c != 10:
			self.midiPending.append(('TNAME', offset, self.name.title() ))
	
		if gbl.debug:
			print "MIDI Channel %s assigned to %s." % (self.channel, self.name)
			

	def setChShare(self, ln, warn=1):
		""" Share midi-channel setting. """

		if self.channel:	# If channel already assigned, ignore
			return
			
		""" Get name of track to share with and make sure it exists.
			If not, trackAlloc() will create the track. Do some
			sanity checks and ensure that the shared track has
			a channel assigned.			
		"""
		
		sc = ln.upper()
		
		MMAalloc.trackAlloc(sc, 1)
		
		if not sc in gbl.tnames:
			error("Channel '%s' does not exist. No such name." % sc)
		
		if sc == self.name:
			error("%s can't share MIDI channel with itself." % sc)
		
		
		if not gbl.tnames[sc].channel:
			gbl.tnames[sc].setChannel()

		schannel = gbl.tnames[sc].channel

		if not schannel:
			error("CHShare attempted to assign MIDI channel for %s, but "
					"none avaiable." %  self.name)

		
		# Actually do the assignment
		
		self.channel = schannel

		warning("%s and %s now share MIDI channel %s" %
				(sc, self.name, self.channel))

		# Update the avail. lists
			
		gbl.midiAssigns[self.channel].append(self.name)
		gbl.midiAvail[self.channel]+=1

					
	def setChannelVolume(self, v):
		""" LowLevel MIDI command. Set Channel Voice. """
		
		self.midiPending.append(( "CVOLUME", gbl.tickOffset, v) )

		if gbl.debug:
			print "Set %s MIDIChannelVolume to %s" % (self.name, v)

				
	def setPan(self, ln):
		""" Set MIDI Pan for this track. """
		
		v = stoi(ln[0], "Expecting integer value 0..127") 
	
		if v<0 or v>127:
			error("PAN value must be 0..127")

		self.midiPending.append( ("PAN", gbl.tickOffset, v))

		if gbl.debug:
			print "Set %s MIDIPan to %s" % (self.name, v)


		
	def setGlis(self, ln):
		""" Set MIDI Glis for this track. """
		
		v = stoi(ln, "Expecting integer for Portamento")	
		
		if v<0 or v>127:
			error("Value for Portamento must be 0..127")
			
		self.midiPending.append( ("GLIS", gbl.tickOffset, v))

		if gbl.debug:
			print "Set %s MIDIPortamento to %s" % (self.name, v)



	def setStrum(self, ln):
		""" Set Strum time. """

		# Strum is only valid for CHORD tracks.
		
		if self.vtype != "CHORD":
			error( "Strum is only valid in Chord tracks, you tried to " 
				"set it in a %s track." % self.name)

		ln=self.lnExpand(ln, 'Strum')
		tmp = []
		
		for n in ln:
			n = stoi(n, "Argument for %s Strum must be an integer" \
					% self.name)
		
			if n < 0 or n > 100:
				error("Strum %s out-of-range; must be 0..100." % n)
			
			tmp.append( n )
			
		self.strum = seqBump( tmp )
		
		if gbl.debug:
			print "Set %s Strum to %s" % (self.name, self.strum)


	def setTone(self, ln):
		""" Set Tone. Error trap, only drum tracks have tone. """
		
		error("Tone command not supported for %s track." % self.name)

		
	def setOn(self):
		""" Turn ON track. """
		
		self.disable = 0
		self.ssvoice = -1

		if gbl.debug:
			print "%s Enabled" % self.name


		
	def setOff(self):
		""" Turn OFF track. """
		
		self.disable = 1

		if gbl.debug:
			print "%s Disabled" % self.name

	

	def setRVolume(self, ln):
		""" Set the volume randomizer for a track. """

		ln = self.lnExpand(ln, 'RVolume')

		tmp =[]
		
		for n in ln:
			
			n = stoi(n, "Argument for %s RVolume must be a value." \
					% self.name)
					
			if n < 0 or n > 100:
				error("RVolume %s out-of-range; must be 0..100." % n)
						
			if n > 30:
				warning("%s is a large RVolume value!" % n)
					
			tmp.append( n )

			
		self.rVolume = seqBump( tmp )

		if gbl.debug:
			print "Set %s Rvolume to " % self.name,
			printList(ln)


	def setRSkip(self, ln):
		""" Set the note random skip factor for a track. """

		ln = self.lnExpand(ln, 'RSkip')

		tmp = []
		for n in ln:

			n = stoi(n, "Expecting integer after in RSkip")
			
			if n < 0 or n > 99:
				error("RSkip arg must be 0..99")
			
			tmp.append(n) 

		self.rSkip = seqBump( tmp )
			
		if gbl.debug:
			print "Set %s RSkip to " % self.name,
			printList(ln)



	def setRTime(self, ln):
		""" Set the timing randomizer for a track. """
		
		ln=self.lnExpand(ln,  'RTime')
		tmp=[]
		
		for n in ln:
			n=stoi(n, "Expecting an integer for Rtime")
			if n < 0 or n > 100:
				error("RTime %s out-of-range; must be 0..100." % n)
			
			tmp.append(n)
				
		self.rTime = seqBump( tmp )

		if gbl.debug:
			print "Set %s RTime to " % self.name,
			printList(ln)

		
	def setRnd(self):
		""" Enable random pattern selection from sequence."""
		
		self.seqRnd = 1

		if gbl.debug:
			print "Set %s SeqRnd." % self.name

		
	def setNoRnd(self):
		""" Disable random pattern selection from sequence."""

		self.seqRnd = 0

		if gbl.debug:
			print "Cleared %s SeqRnd." % self.name


	def setDirection(self, ln):
		""" Set scale direction. """
		
		ln = self.lnExpand(ln, "Direction")
		
		vald = ('UP', 'DOWN', 'BOTH', 'RANDOM')
		tmp = []
		for n in ln:
			n = n.upper()
			if not n in vald:
				error("Unknown %s Direction. Only '%s' are valid." \
					% (self.name, ' '.join(vald) ))
			tmp.append(n)
			
		self.direction = seqBump( tmp )
		if self.vtype == 'SCALE':
			self.lastChord = None
			self.lastNote = -1
	

		if gbl.debug:
			print "Set %s Direction to " % self.name,
			printList(ln)


	def setScaletype(self, ln):
		""" Set scale type. """
		
		ln = self.lnExpand(ln, "ScaleType")
		
		vald = ( 'CHROMATIC', 'AUTO')
		tmp = []
		
		for n in ln:
			n = n.upper()
			if not n in vald:
				error("Unknown %s ScaleType. Only '%s' are valid." \
					% (self.name, ' '.join(vald) ))
			tmp.append(n)
			
		if self.vtype == 'SCALE':
			self.scaleType = seqBump( tmp )
	
			self.lastChord = None
			self.lastNote = -1
	
		if gbl.debug:
			if self.vtype=='SCALE':
				print "Set %s ScaleType to " % self.name,
				printList(ln)
			else:
				print "Set %s ScaleType INGORED" % self.name


	
	def setInvert(self, ln):
		""" Set inversion for track.
			
 			This can be applied to any track,
			but has no effect in drum tracks. It inverts the chord
			by one rotation for each value.
		"""
		
		ln=self.lnExpand(ln, "Invert")
		
		vwarn = 0
		tmp = []
		
		for n in ln:
			n = stoi(n, "Argument for %s Invert must be an integer" \
					% self.name)
			
			if n and self.vtype=='CHORD' and self.voicing.mode:
				vwarn = 1
				
			tmp.append(n)
			
		self.invert = seqBump( tmp )

		if self.vtype not in ("CHORD", "ARPEGGIO"):
			warning ("Invert is ignored in %s tracks." % self.vtype)
		
		if vwarn:
			warning("Setting both Voicing Mode and Invert is not a good idea")
		
		if gbl.debug:
			print "Set %s Invert to " % self.name,
			printList(ln)

							
	def setOctave(self, ln):
		""" Set the octave for a track. """
		
		ln=self.lnExpand(ln, 'Octave')
		tmp = []
		
		for n in ln:
			n = stoi(n, "Argument for %s Octave must be an integer" \
					% self.name)
			if n < 0 or n > 10:
				error("Octave %s out-of-range; must be 0..10." % n)

			tmp.append(n * 12)
		
		self.octave = seqBump( tmp )
		
		if gbl.debug:
			print "Set %s Octave to" % self.name,
			for i in self.octave:
				print i/12,
			print

	def setHarmony(self, ln):
		""" Set the harmony. """
		
		
		ln=self.lnExpand(ln, 'Harmony')
		tmp = []
		
		for n in ln:
			n = n.upper()
			if n in ( '-', '-0'):
				n = None
			
			tmp.append(n)

		self.harmony = seqBump( tmp )

		if self.vtype not in ( 'SOLO', 'MELODY', 'BASS',
				'WALK', 'SCALE', 'ARPEGGIO'):	
			warning("Harmony setting for %s track ignored" % self.vtype)
			
		if gbl.debug:
			print "Set %s Harmony to" % self.name,
			printList(self.harmony)


	def setHarmonyOnly(self, ln):
		""" Set the harmony only. """
		
		
		ln=self.lnExpand(ln, 'HarmonyOnly')
		tmp = []
		
		for n in ln:
			n = n.upper()
			if n in ('-', '0'):
				n = None
			
			tmp.append(n)

		self.harmony = seqBump( tmp )
		self.harmonyOnly = seqBump( tmp )
		
		if self.vtype in ( 'CHORD', 'DRUM'):	
			warning("HarmonyOnly setting for %s track ignored" % self.vtype)
			
		if gbl.debug:
			print "Set %s HarmonyOnly to" % self.name,
			printList(self.harmonyOnly)


	def setSeqSize(self):
		""" Expand existing pattern list. """
		
		if self.sequence:
			self.sequence   = seqBump(self.sequence)
		if self.midiVoice:
			self.midiVoice  = seqBump(self.midiVoice)
		if self.midiSeq:
			self.midiSeq    = seqBump(self.midiSeq)
		self.invert     = seqBump(self.invert)
		self.artic      = seqBump(self.artic)
		self.volume     = seqBump(self.volume)
		self.voice      = seqBump(self.voice)
		self.rVolume    = seqBump(self.rVolume)
		self.rSkip      = seqBump(self.rSkip)
		self.rTime      = seqBump(self.rTime)
		self.strum      = seqBump(self.strum)
		self.octave     = seqBump(self.octave)
		self.harmony    = seqBump(self.harmony)
		self.harmonyOnly= seqBump(self.harmonyOnly)
		self.direction  = seqBump(self.direction)
		self.scaleType  = seqBump(self.scaleType)
		self.compress   = seqBump(self.compress)
		self.chordRange = seqBump(self.chordRange)
		self.duplicate  = seqBump(self.duplicate)
		self.dupRoot    = seqBump(self.dupRoot)
		self.unify      = seqBump(self.unify)

		if self.vtype == "DRUM":
			self.toneList = seqBump(self.toneList)


	def setVoice(self, ln):
		""" Set the voice for a track.
		
			Note, this just sets flags, the voice is set in bar().
			ln[] is not nesc. set to the correct length.
		"""

		ln=self.lnExpand(ln, 'Voice')

		tmp = []
		
		for n in ln:
			n = MMAtranslate.vtable.get(n)
			a=MMAmidi.instToValue(n)

			if a < 0:
				a=stoi(n, "Expecting a valid voice name or value, "
					"not '%s'" % n)
				if a <0 or a > 127:
					error("Voice must be 0..127.")
			tmp.append(a)

		self.voice = seqBump( tmp )

		if gbl.debug:
			print "Set %s Voice to: " % self.name,
			for a in self.voice:
				print MMAmidi.valueToInst(a),
			print


	def setMidiClear(self, ln):
		""" Set MIDIclear sequences. """


		if ln[0] in 'zZ-':
			self.midiClear = None
		else:
			self.midiClear = MMAmdefine.mdef.get(ln[0])
				
		if gbl.debug:
			print "%s MIDIClear: %s" % (self.name,
					self.midiSeqFmt(self.midiClear))
		
		
	def doMidiClear(self):
		""" Reset MIDI settings. """

		if self.midiSent:
			if  not self.midiClear:
				warning("%s: Midi data has been inserted with MIDIVoice/Seq "
					"but no MIDIClear data is present." % self.name)
				
			else:
				for i in self.midiClear:
					gbl.mtrks[self.channel].addCtl(gbl.tickOffset, i[1])
	
			self.midiSent = 0	
	
	
	def setMidiSeq(self, ln):
		""" Set a midi sequence for a track.
		
			This is sent for every bar. Syntax is:
				<beat> <ctrl> hh .. ; ...
				
			or a single '-' to disable.
		"""
	
		ln = self.lnExpand(ln, 'MIDISeq')
		seq = []	
		for a in ln:
			if a in 'zZ-':
				seq.append(None)
			else:
				seq.append(MMAmdefine.mdef.get(a.upper()))
	
		if seq.count(None) == len(seq):
			self.midiSeq = []
		else:
			self.midiSeq = seqBump( seq )

		if gbl.debug:
			print "%s MIDISeq:" % self.name,
			for l in seq:
				print '{ %s }' % self.midiSeqFmt(l),
			print


	def setMidiVoice(self, ln):
		""" Set a MIDI sequence for a track.
		
			This is sent whenever we send a VOICE. Syntax is:
				<beat> <ctrl> hh .. ; ...
				
			or a single '-' to disable.
		"""
		
		ln = self.lnExpand(ln, 'MIDIVoice')

		seq = []
		for a in ln:
			if a in 'zZ':
				seq.append(None)
			else:
				seq.append(MMAmdefine.mdef.get(a.upper()))

		if seq.count(None) == len(seq):
			self.midiVoice = []
		else:
			self.midiVoice = seqBump( seq )


		if gbl.debug:
			print "%s MIDIVoice:" % self.name,
			for l in seq:
				print '{ %s }' % self.midiSeqFmt(l),
			print



	def midiSeqFmt(self, lst):
		""" Used by setMidiVoice/Clear/Seq for debugging format. """
		
		if lst == None:
			return ''
		ret=''
		for i in lst:
			ret += "%s %s 0x%02x ; " % (i[0],
				MMAmidi.valueToCtrl(ord(i[1][0])),
				ord(i[1][1])) 
		return ret.rstrip("; ")


	def setVolume(self, ln):
		""" Set the volume for a pattern.
			ln - list of volume names (pp, mf, etc)
			ln[] not nesc. correct length
		"""

		ln=self.lnExpand(ln, 'Volume')
		tmp = []
		
		d=gbl.vols
		for n in ln:
			a = n.upper()	

			if not a in d:
				error("Expecting a valid volume, not '%s'" % n)
			tmp.append( d[a] )
			
		self.volume = seqBump( tmp )
			
		if gbl.debug:
			print "Set %s Volume to " % self.name,
			for a in self.volume:
				print keyLookup(d,a),
			print



	def setMallet(self, ln):
		""" Set the note repeat/mallet value. """
	
		error("Mallet not supported in %s track." % self.name)
		
		
	def setAccent(self, ln):
		""" Set the accent values. """
	
		self.accent = []

		if len(ln):
			if  len(ln)/2*2 != len(ln):
				error("Use: %s Accent Beat Percentage [...]" % self.name)
			
	
		
			for b, v in zip(ln[::2], ln[1::2]):
				b=self.setBarOffset( b )
				v=stof(v, "Bbeat offset must be a value, not '%s'." % v)
				if v<-100 or v>100:
					error("Velocity adjustment (as percentage) must "
						"be -100..100, not '%s'." % v)
				
				self.accent.append( (b, v/100) )
		
		if gbl.debug:
			print "%s Accent: " % self.name,
			for b,v in self.accent:
				print '%s=%s ' % (1+(b/float(gbl.BperQ)), v*100),
			print
			
	def setArtic(self, ln):
		""" Set the note articuation value. """
	
		ln=self.lnExpand(ln, 'Articulate')
		tmp = []

		for n in ln:
			a = stoi(n, "Expecting value in articulation setting.")
			if a < 1 or a > 100:
				error("Articulation setting must be 1..100, "
					"not %s." % a)
			
			tmp.append(a)
			
		self.artic = seqBump( tmp )

		if gbl.debug:
			print "Set %s Articulation to " % self.name,
			printList(ln)


	def setUnify(self, ln):
		""" Set unify. """
		
		ln = self.lnExpand(ln, "Unify")
		tmp = []
		
		for n in ln:
			n=n.upper()
			if n  in ( 'ON',  '1'):
				n=1
			elif n in( 'OFF', '0'):
				n=None
			else:
				error("Unify accepts ON | OFF | 0 | 1")
			
			tmp.append( n )
				
			
		self.unify = seqBump( tmp )

		if gbl.debug:
			print "Set %s Unify to " % self.name,
			printList(self.unify)


				
	def lnExpand(self, ln, cmd):
		""" Validate and expand a list passed to a set command. """
		
		if len(ln) > gbl.seqSize:
			warning("%s list truncated to %s patterns." % 
				(self.name, gbl.seqSize) )
			
		last = None

		for i,n  in enumerate(ln):
			if n == '/':
				if not last:
					error ("You cannot use a '/' as the first item "
						"in a %s list." % cmd)
				else:
					ln[i] = last
			else:
				last = n

		return ln



	def copySettings(self, cp):
		""" Copy the voicing from a 2nd voice to the current one. """
	
		if not cp in gbl.tnames:
			error("CopySettings does not know track '%s'." % cp)
			
		cp=gbl.tnames[cp]
		
		if cp.vtype != self.vtype:
			error("Tracks must be of same type for copy ... "
				"%s and %s aren't." % (self.name, cp.name))
				
		self.volume		= cp.volume[:]
		self.rVolume	= cp.rVolume[:]
		self.accent     = cp.accent[:]
		self.rSkip		= cp.rSkip[:]
		self.rTime		= cp.rTime[:]
		self.strum		= cp.strum[:]
		self.octave		= cp.octave[:]
		self.harmony    = cp.harmony[:]
		self.harmonyOnly= cp.harmonyOnly[:]
		self.direction	= cp.direction[:]
		self.scaleType	= cp.scaleType[:]
		self.voice		= cp.voice[:]
		self.invert		= cp.invert[:]
		self.artic		= cp.artic[:]
		self.compress	= cp.compress[:]
			
		if self.vtype == 'DRUM':
			self.toneList = cp.toneList[:]
		

		if gbl.debug:
			print "Settings from %s copied to %s." % (cp.name, self.name)
	


	##################################################
	## Save/restore grooves
						
	def saveGroove(self, gname):
		""" Define a groove.
		
			Called by the 'DefGroove Name'. This is called for
			each track. 
		
			If 'gname' is already defined it is overwritten.	
		
			Note aux. function which may be defined for each track type.
		"""
		
		self.grooves[gname] = {
			'ACCENT':   self.accent[:],
			'ARTIC':    self.artic[:],
			'COMPRESS': self.compress[:],
			'DIR':      self.direction[:],
			'DUPLICATE':self.duplicate[:],
			'DUPROOT':  self.dupRoot[:],
			'HARMONY':  self.harmony[:],
			'HARMONYO': self.harmonyOnly[:],
			'INVERT':   self.invert[:],
			'LIMIT':    self.chordLimit,
			'RANGE':    self.chordRange[:],
			'OCTAVE':   self.octave[:],
			'RSKIP':    self.rSkip[:],
			'RTIME':    self.rTime[:],
			'RVOLUME':  self.rVolume[:],
			'SCALE':    self.scaleType[:],
			'SEQ':      self.sequence[:],
			'SEQRND':   self.seqRnd,
			'STRUM':    self.strum[:],
			'VOICE':    self.voice[:],
			'VOLUME':   self.volume[:],
			'UNIFY':    self.unify[:],
			'MIDISEQ':  self.midiSeq[:],
			'MIDIVOICE':self.midiVoice[:],
			'MIDICLEAR':self.midiClear[:] }			
			

		if self.vtype == 'CHORD':
			self.grooves[gname]['VMODE'] =  copy.deepcopy(self.voicing)
			
		if self.vtype == 'DRUM':
			self.grooves[gname]['TONES'] = self.toneList[:]

		if self.vtype == 'MELODY':
			self.grooves[gname]['MALLET'] =  self.mallet
			self.grooves[gname]['MALLETDK'] =  self.malletDecay
				
	def restoreGroove(self, gname):
		""" Restore a defined groove. """

		g = self.grooves[gname]

		self.sequence   =  g['SEQ']
		self.volume     =  g['VOLUME']
		self.accent     =  g['ACCENT']
		self.rTime      =  g['RTIME']
		self.rVolume    =  g['RVOLUME']
		self.rSkip      =  g['RSKIP']
		self.strum      =  g['STRUM']
		self.octave     =  g['OCTAVE']
		self.voice      =  g['VOICE']
		self.harmonyOnly=  g['HARMONYO']
		self.harmony    =  g['HARMONY']
		self.direction  =  g['DIR']
		self.scaleType  =  g['SCALE']
		self.invert     =  g['INVERT']
		self.artic      =  g['ARTIC']
		self.seqRnd     =  g['SEQRND' ]
		self.compress   =  g['COMPRESS']
		self.chordRange =  g['RANGE']
		self.duplicate  =  g['DUPLICATE']
		self.dupRoot    =  g['DUPROOT']
		self.chordLimit =  g['LIMIT']
		self.unify      =  g['UNIFY']
		self.midiClear  =  g['MIDICLEAR']
		self.midiSeq    =  g['MIDISEQ']
		self.midiVoice  =  g['MIDIVOICE']


		if self.vtype == 'CHORD':
			self.voicing    =  g['VMODE']
			
		if self.vtype == 'DRUM':
			self.toneList = g['TONES']	

		if self.vtype == 'MELODY':
			self.mallet = g['MALLET']				
			self.malletDecay = g['MALLETDK']				


		"""	It's quite possible that the track was created after
			the groove was saved. This means that the data restored
			was just the default stuff inserted when the track
			was created ... which is fine, but the sequence size
			isn't necs. right.
		"""
	
		if len(self.octave) < gbl.seqSize:
			self.setSeqSize()
		
		self.doMidiClear()				
			

			
	####################################
	## Sequence functions
	
	def setSequence(self, ln):
		""" Set the sequence for a track. """

		base=self.vtype

		tmp = []
		for a in ln:
			a=a.upper()
			if a in  'Zz-':
				a = None
				
			elif a == '/':
				if not tmp:
					error("The first pattern in a sequence cannot be '/'.")
				a = tmp[-1]
				
			else:
				a = (base, a)
				if not a in pats:
					error("Track %s does not have pattern '%s'." 
						% (self.name, a[1]) )
			tmp.append(a)
						
		ln = self.lnExpand(tmp, 'Sequence')

		""" Step though the list of patterns and set the sequence.
			There's a bit of Python reference trickery here. If we
			set a sequence with something like:
			
				Bass Sequence B1 B2
				
			the bass sequence is set with pointers to the existing
			patterns defined for B1 and B2. Now, if we later change
			the definitions for B1 or B2, the stored pointer DOEN'T
			change. So, changing pattern definitions has NO EFFECT.
		"""
		
		tmp=[]
		for n in ln:
			if n:
				tmp.append(pats[n])
			else:
				tmp.append(None)
		
		if tmp.count(None) == len(tmp):
			self.sequence = []
		else:
			self.sequence = seqBump( tmp )
		
		if gbl.seqshow:
			print "%s sequence set:" % self.name,
			for a in ln:
				if not a: print "-",
				else: print a[1],
			print

		
	def clearSequence(self):
		""" Clear sequence for track.
			This is also called from __init__() to set the 
			initial defaults for each track.
		"""

		if self.vtype != 'SOLO' or not self.inited:
			self.sequence      =  ()
			self.seqRnd        =  0
			self.scaleType     =  ('AUTO',)
			self.rVolume       =  (0,)
			self.rSkip         =  (0,)
			self.rTime         =  (0,)
			self.octave        =  (4 * 12,)
			self.voice         =  (0,)
			self.chordRange    =  (1,)
			self.harmony       =  (None,)
			self.harmonyOnly   =  (None,)
			self.strum         =  (0,)		
			self.volume        =  (gbl.vols['MF'],)
			self.compress      =  (0,)
			self.duplicate     =  (0,)
			self.dupRoot       =  (0,)
			self.chordLimit    =  0
			self.invert        =  (0,)			
			self.lastChord     =  []	
			self.accent        =  []
			self.unify         =  (None,)
			self.midiClear     =  ( )
			self.midiSeq       =  ( )
			self.midiVoice     =  ( )


					
		if self.riff:
			warning("%s sequence clear deleting unused riff" % self.name)
		self.riff = []
		
		if self.vtype == 'CHORD':
			self.voicing   = Voicing()
			self.direction = ('UP',)
		else:
			self.direction  =  ('BOTH',)
				
		self.setSeqSize()


	############################
	### Pattern functions
	############################
		

	def definePattern(self, name, ln):
		""" Define a Pattern. 

		    All patterns are stored in pats{}. The keys for this
		    are tuples -- (track type, pattern name).

		"""
		
		name = name.upper()
		slot = (self.vtype,name)
		
		# This is just for the debug code
		
		if name.startswith('_'):
			redef = "dynamic define"
		elif slot in pats:
			redef = name + ' redefined'
		else:
			redef = name + ' created'
		
		ln = ln.rstrip('; ')    # Delete optional trailing  ';' & WS
		pats[slot] = self.defPatRiff(ln)
		
		if gbl.pshow:
			print "%s pattern %s:" % (self.name.title(), redef )
			self.printPattern(pats[slot])


	def setRiff(self, ln):
		""" Define and set a Riff. """

		if self.riff:
			warning("%s overwriting unused riff." % self.name)
			self.riff=[]
			
		if len(ln) == 1 and (ln[0] in ('Z','z','-')):
			self.riff = []
			if gbl.pshow:
				print "%s Riff cancelled." % self.name
				
		else: 
			self.riff = [self.defPatRiff(ln)]
			if gbl.pshow:
				print "%s Riff:" % self.name
				self.printPattern(self.riff[-1])


	def setMultiRiff(self, ln):
		""" Define and set a multi-riff. 
		
			Same as a riff, but this stacks.
		"""

		if len(ln) == 1 and (ln[0] in ('Z','z','-')):
			error("Can't delete a Riff with 'z' or '-' in multi-mode")

		self.riff.append(self.defPatRiff(ln))
		if gbl.pshow:
			print "%s RiffAppend:" % self.name
			self.printPattern(self.riff[-1])

		

	def defPatRiff(self, ln):
		""" Worker function to define pattern. Shared by definePattern()
			and setRiff().
		"""

		def mulPatRiff(oldpat, fact):
			""" Multiply a pattern. """
			
			fact = stoi(fact, "The multiplier arg must be an "
				"integer not '%s'." % fact)
		
			if fact<1 or fact >100:
				error("The multiplier arg must be in the range 2 to 100.")

		
			""" Make N copies of pattern, adjusted so that the new copy has
				all note lengths and start times  adjusted.
				 eg: [[1, 2, 66], [3, 2, 88]]  * 2
				     becomes [[1,4,66], [2,4,88], [3,4,66], [4,4,88]].
			"""
				
			new = []
			add = 0
			step = (gbl.BperQ * gbl.QperBar)/fact

			for n in range(fact):
				orig = copy.deepcopy(oldpat)
				for z in orig:
					z.offset = (z.offset / fact) + add
					z.duration /= fact
					if z.duration < 1:
						z.duration = 1
	
					new.append(z)
				add += step
		
			return tuple( new )
		
	
		def shiftPatRiff(oldpat, fact):
			
			fact = stof(fact, "The shift arg must be a value, "
				"not '%s'." % fact)
		
			# Adjust all the beat offsets
		
			new = copy.deepcopy(oldpat)				
			max = gbl.BperQ * (gbl.QperBar)
			for n in new:
				n.offset += fact * gbl.BperQ
				if n.offset < 0 or n.offset > max:
					error("Pattern shift with factor %f has resulted in an "
						"illegal offset." % fact )
	
			return  tuple( new )
				
		def patsort(c1, c2):
			""" Sort a pattern tuple. """
		
			if c1.offset < c2.offset: return -1
			if c1.offset == c2.offset: return 0
			else: return 1
	
				
		### Start of main function...
		
		# Convert the string to list...
		#  "1 2 3; 4 5 6" --->  [ [1,2,3], [4,5,6] ]

		p = []
		ln = ln.upper().split(';')
		for l in ln:
			p.append(l.split())
	
		plist=[]


		for ev in p:
				
			more=[]
			for i,e in enumerate(ev):
				if e.upper() in ('SHIFT', '*'):
 					if i == 0:
						error("Pattern definition can't start with"
							"SHIFT or *")
					more = ev[i:]
					ev=ev[:i]
					break
					
			if len(ev) == 1:
				nm = ev[0]

				if (self.vtype,nm) in pats:
					if nm.startswith('_'):
						error("You can't use a pattern name beginning"
							" with an underscore.")
					pt = pats[(self.vtype,nm)]
					
				else:
					error("%s is not an existing %s pattern." \
						% (nm, self.vtype.title()) )
						
			else:
				pt = [self.getPgroup(ev)]

			while more:
				cmd = more.pop(0)
				if cmd not in ('SHIFT', '*'):
					error("Expecting SHIFT or *, not '%s'." % cmd)
					
				if not more:
					error("Expecting factor after %s" % cmd)
				if cmd == 'SHIFT':
					pt = shiftPatRiff(pt, more.pop(0))
				elif cmd == '*':
					pt = mulPatRiff(pt, more.pop(0))
				
			plist.extend(pt)			

		
		plist.sort(patsort)

		return tuple( plist )

	
					
	def printPattern(self, pat):
		""" Print a pattern. Used by debugging code."""
		
		s=[]
		for p in pat:
			s.append(" %2.2f %2.0f" % (1+(p.offset/float(gbl.BperQ)),
				p.duration))
				
			if self.vtype == 'CHORD':
				for a in p.vol:
					s.append( " %2.0f" % a)

			elif self.vtype == 'BASS':
				s.append( " %2.0f %2.0f" % (p.noteoffset, p.vol ) )
			
			elif self.vtype == 'ARPEGGIO':
				s.append( " %2.0f " % p.vol )
				
			elif self.vtype == 'DRUM':
				s.append(" %2.0f" %  p.vol)
			
			elif self.vtype == 'WALK':
				s.append(" %2.0f" % p.vol )
				
			s.append(' ;')
			s.append('\n')
		s[-2]='  '
		print "".join(s)

	
	#########################
	## Music processing
	#########################
		
	def bar(self, ctable):
		""" Process a bar of music. """

		
		if 	self.disable:
			return

		""" Decide which seq to use. This is either the current
			seqCount, or if SeqRnd has been set for the track
			it is a random pattern in the sequence. 

			The class variable self.seq is set to the sequence to
			use. 
		"""
		
		if self.seqRnd:
			self.seq = random.randrange(gbl.seqSize)
		else:
			self.seq = gbl.seqCount
		
		sc = self.seq

		""" Get pattern for this sequence. Either a Riff or a Pattern. """
		
		if self.riff:
			pattern = self.riff.pop(0)
	
		else:
			if not self.sequence:
				return
				
			pattern = self.sequence[sc]

			if not pattern:
				return
	
						
		""" MIDI Channel assignment. If no channel is assigned try
			to find an unused number and assign that.
		"""
		
		if not self.channel:
			self.setChannel()
			
		# We are ready to create musical data. 1st do pending midi commands.
		
		self.clearPending()	

		""" 1st pass for MIDIVOICE. There's a separate slot for
			each bar in the sequence, plus the data can be sent
			before or after 'voice' commands. This first loop
			sends MIDIVOICE data with an offset of 0. Note, we
			don't set the value for 'self.smidiVoice' until we
			do this again, later. All this is needed since some
			MIDIVOICE commands NEED to be sent BEFORE voice selection,
			and others AFTER.
		"""
		
		if self.midiVoice:
			v = self.midiVoice[sc]
			if v and v != self.smidiVoice:
				for i in v:
					if not i[0]:
						gbl.mtrks[self.channel].addCtl(gbl.tickOffset, i[1])
		
		# Set the voice in the midi track if not previously done.

		v=self.voice[sc]
		if v != self.ssvoice:
			gbl.mtrks[self.channel].addProgChange( gbl.tickOffset,  v)
			self.ssvoice = v
		
			# Mark ssvoice also in shared tracks

			for a in gbl.midiAssigns[self.channel]:
				if gbl.tnames.has_key(a):
					gbl.tnames[a].ssvoice = v
						
			if gbl.debug:
				print "Track %s Voice %s inserted." \
					% (self.name, MMAmidi.valueToInst(v) )

		""" Our 2nd stab at MIDIVOICE. This time any sequences
			with offsets >0 are sent. AND the smidiVoice and midiSent
			variables are set.
		"""
		
		if self.midiVoice:
			v = self.midiVoice[sc]
			if v and v != self.smidiVoice:
				for i in v:
					if i[0]:
						gbl.mtrks[self.channel].addCtl(gbl.tickOffset, i[1])
				self.smidiVoice = v
				self.midiSent = 1  # used by MIDICLEAR	
					

		# Do MIDISeq for this voice
		
		if self.midiSeq:
			l = self.midiSeq[sc]
			if l:
				for i in l:
					gbl.mtrks[self.channel].addCtl( getOffset(i[0]), i[1] )
				self.midiSent = 1
			
		self.trackBar(pattern, ctable)


	def clearPending(self):
	
	
		while self.midiPending:
			c, off, v = self.midiPending.pop(0)
			if c == 'TNAME':
				gbl.mtrks[self.channel].addTrkName(off, v)
				if gbl.debug:
					print "%s Track name inserted at offset %s." % \
						(self.name, off)		

			
			elif c == 'GLIS':
				gbl.mtrks[self.channel].addGlis(off, v)
				if gbl.debug:
					print "%s Glis at offset %s set to %s." % \
						(self.name, off, ord(chr(v)))		
				
			elif c == 'PAN':
				gbl.mtrks[self.channel].addPan(off, v)
				if gbl.debug:
					print "%s Pan at offset %s set to %s." % \
						(self.name, off, v)		
				
			elif c == 'CVOLUME':
				gbl.mtrks[self.channel].addChannelVol(off, v)
				if gbl.debug:
					print "%s ChannelVolume at offset %s set to %s" % \
						(self.name, off, v)

			else:
				error("Unknown midi command pending. Call Bob.")

	
		
	def getChordInPos( self, offset, ctable):
		""" Compare an offset to a list of ctables and return
			the table entry active for the given beat. 
			
			We assume that the first offset in 'ctable' is 0!
			We assme that 'offset' is >= 0!
	
			Returns a ctable.
		"""
		
		for i in range(len(ctable)-1, -1, -1):	# reverse order
			if offset >= ctable[i].offset:
				break
		return ctable[i]



	def adjustVolume(self, v, beat):
		""" Adjust a note volume based on the track and global volume
			setting.
		"""

		if not v:
			return 0
		
		sc = self.seq
		
		if self.rSkip[sc] and random.random() * 100 < self.rSkip[sc]:
			return 0

		v =  (v * self.volume[sc] * gbl.volume)	/ 10000

		for b,a in self.accent:
			if b==beat:
				v += v * a
			
		if self.rVolume[sc]:
			a = int((v * self.rVolume[sc])/100)
			if a:
				v += random.randrange(-a, a)
				
		
		if v > 127:
			v = 127
		elif  v < 1:
			v = 1
			
		return int(v)
		
			
	def adjustNote(self, n):
		""" Adjust a note for a given octave/transposition.
			Ensure that the note is in range.
		"""

		n += self.octave[self.seq] + gbl.transpose
		
		while n < 0:
			n += 12
		while n > 127:
			n -= 12
		
		return n

	
	def setBarOffset(self, v):
		""" Convert a string into a valid bar offset in midi ticks. """

		v=stof(v, "Value for %s bar offset must be integer/float" % self.name)	
		
		if v < 1:
			error("Defining %s Pattern, bar offset must be 1 or greater." %
				 self.name)
				 
		if v >= gbl.QperBar+1:
			error("Defining %s Pattern, bar offset must be less than %s." %
				(self.name, gbl.QperBar + 1))
				
				
		return int((v-1) * gbl.BperQ)
		
		
	def getDur(self, d):
		""" Return the adjusted duration for a note. 
		
			The adjustment makes notes more staccato. Valid
			adjustments are 1 to 100. 100 is not recommended.
		"""

		d = (d * self.artic[self.seq]) / 100
		if not d:
			d = 1
			
		return d
	
