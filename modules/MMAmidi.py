# MMAmidi.py

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

""" English names for midi instruments and drums.
	
	These tables are used by the pattern classes to
	convert inst/drum names to midi values and by the
	doc routines to print tables.
"""

# The drum names are valid for tones 27 to 87

drumNames=[
	'HighQ', 'Slap', 'ScratchPush', 'ScratchPull',
	'Sticks', 'SquareClick', 'MetronomeClick',
	'MetronomeBell', 'KickDrum2', 'KickDrum1',
	'SideKick', 'SnareDrum1', 'HandClap',
	'SnareDrum2', 'LowTom2', 'ClosedHiHat',
	'LowTom1', 'PedalHiHat', 'MidTom2', 'OpenHiHat',
	'MidTom1', 'HighTom2', 'CrashCymbal1',
	'HighTom1', 'RideCymbal1', 'ChineseCymbal',
	'RideBell', 'Tambourine', 'SplashCymbal',
	'CowBell', 'CrashCymbal2', 'VibraSlap',
	'RideCymbal2', 'HighBongo', 'LowBongo',
	'MuteHighConga', 'OpenHighConga', 'LowConga',
	'HighTimbale', 'LowTimbale', 'HighAgogo',
	'LowAgogo', 'Cabasa', 'Maracas',
	'ShortHiWhistle', 'LongLowWhistle', 'ShortGuiro',
	'LongGuiro', 'Claves', 'HighWoodBlock',
	'LowWoodBlock', 'MuteCuica', 'OpenCuica',
	'MuteTriangle', 'OpenTriangle', 'Shaker',
	'JingleBell', 'Castanets', 'MuteSudro',
	'OpenSudro' ]

upperDrumNames = [name.upper() for name in drumNames]


voiceNames=[
	'Piano1', 'Piano2','Piano3',
	'Honky-TonkPiano', 'RhodesPiano', 'EPiano',
	'HarpsiChord', 'Clavinet', 'Celesta',
	'Glockenspiel', 'MusicBox', 'Vibraphone',
	'Marimba', 'Xylophone', 'TubularBells', 'Santur',
	'Organ1', 'Organ2', 'Organ3', 'ChurchOrgan',
	'ReedOrgan', 'Accordion', 'Harmonica',
	'Bandoneon', 'NylonGuitar', 'SteelGuitar',
	'JazzGuitar', 'CleanGuitar', 'MutedGuitar',
	'OverDriveGuitar', 'DistortonGuitar',
	'GuitarHarmonics', 'AcousticBass',
	'FingeredBass', 'PickedBass', 'FretlessBass',
	'SlapBass1', 'SlapBass2', 'SynthBass1',
	'SynthBass2', 'Violin', 'Viola', 'Cello',
	'ContraBass', 'TremoloStrings',
	'PizzicatoString', 'OrchestralHarp', 'Timpani',
	'Strings', 'SlowStrings', 'SynthStrings1',
	'SynthStrings2', 'ChoirAahs', 'VoiceOohs',
	'SynthVox', 'OrchestraHit', 'Trumpet',
	'Trombone', 'Tuba', 'MutedTrumpet', 'FrenchHorn',
	'BrassSection', 'SynthBrass1', 'SynthBrass2',
	'SopranoSax', 'AltoSax', 'TenorSax',
	'BaritoneSax', 'Oboe', 'EnglishHorn', 'Bassoon',
	'Clarinet', 'Piccolo', 'Flute', 'Recorder',
	'PanFlute', 'BottleBlow', 'Shakuhachi',
	'Whistle', 'Ocarina', 'SquareWave', 'SawWave',
	'SynCalliope', 'ChifferLead', 'Charang',
	'SoloVoice', '5thSawWave', 'Bass&Lead',
	'Fantasia', 'WarmPad', 'PolySynth', 'SpaceVoice',
	'BowedGlass', 'MetalPad', 'HaloPad', 'SweepPad',
	'IceRain', 'SoundTrack', 'Crystal', 'Atmosphere',
	'Brightness', 'Goblins', 'EchoDrops',
	'StarTheme', 'Sitar', 'Banjo', 'Shamisen',
	'Koto', 'Kalimba', 'BagPipe', 'Fiddle', 'Shanai',
	'TinkleBell', 'AgogoBells', 'SteelDrums',
	'WoodBlock', 'TaikoDrum', 'MelodicTom1',
	'SynthDrum', 'ReverseCymbal', 'GuitarFretNoise',
	'BreathNoise', 'SeaShore', 'BirdTweet',
	'TelephoneRing', 'HelicopterBlade',
	'Applause/Noise', 'GunShot' ]


upperVoiceNames = [name.upper() for name in voiceNames]

ctrlNames = [
	### also see: http://www.midi.org/about-midi/table3.shtml

	### 0-31 Double Precise Controllers
	### MSB (14-bits, 16,384 values)

	'Bank', 'Modulation', 'Breath', 'Ctrl3',
	'Foot', 'Portamento', 'Data', 'Volume',
	'Balance', 'Ctrl9', 'Pan', 'Expression',
	'Effect1', 'Effect2', 'Ctrl14', 'Ctrl15',
	'General1','General2','General3','General4',
	'Ctrl20', 'Ctrl21', 'Ctrl22', 'Ctrl23',
	'Ctrl24', 'Ctrl25', 'Ctrl26', 'Ctrl27',
	'Ctrl28', 'Ctrl29', 'Ctrl30', 'Ctrl31',
	### 32-63  Double Precise Controllers
	### LSB (14-bits, 16,384 values)
	'BankLSB', 'ModulationLSB', 'BreathLSB',
	'Ctrl35', 'FootLSB', 'PortamentoLSB',
	'DataLSB','VolumeLSB','BalanceLSB',
	'Ctrl41','PanLSB','ExpressionLSB',
	'Effect1LSB', 'Effect2LSB','Ctrl46', 'Ctrl47',
	'General1LSB','General2LSB', 'General3LSB',
	'General4LSB', 'Ctrl52','Ctrl53', 'Ctrl54',
	'Ctrl55', 'Ctrl56', 'Ctrl57', 'Ctrl58',
	'Ctrl59', 'Ctrl60', 'Ctrl61', 'Ctrl62',
	'Ctrl63',

	### 64-119 Single Precise Controllers
	### (7-bits, 128 values)

	'Sustain', 'Portamento', 'Sostenuto',
	'SoftPedal', 'Legato', 'Hold2', 'Variation',
	'Resonance', 'ReleaseTime','AttackTime', 'Brightness',
	'DecayTime','VibratoRate','VibratoDepth', 'VibratoDelay',
	'Ctrl79','General5','General6','General7',
	'General8','PortamentoCtrl','Ctrl85','Ctrl86',
	'Ctrl87', 'Ctrl88', 'Ctrl89', 'Ctrl90',
	'Reverb', 'Tremolo', 'Chorus','Detune',
	'Phaser', 'DataInc','DataDec',
	'NonRegLSB', 'NonRegMSB',
	'RegParLSB', 'RegParMSB',
	'Ctrl102','Ctrl103','Ctrl104','Ctrl105',
	'Ctrl106','Ctrl107','Ctrl108','Ctrl109',
	'Ctrl110','Ctrl111','Ctrl112','Ctrl113',
	'Ctrl114','Ctrl115','Ctrl116','Ctrl117',
	'Ctrl118','Ctrl119',

	### 120-127 Channel Mode Messages

	'AllSoundsOff','ResetAll',
	'LocalCtrl','AllNotesOff',
	'OmniOff','OmniOn', 'PolyOff','PolyOn' ]
	
upperCtrlNames = [name.upper() for name in ctrlNames]


def drumToValue(name):
	""" Get the value of the drum tone (-1==error). """
	
	try:
		return  upperDrumNames.index(name.upper()) + 27
	except ValueError:
		return  -1

	
def instToValue(name):
	""" Get the value of the instrument name (-1==error). """
	
	try:
		return  upperVoiceNames.index(name.upper())
	except ValueError:
		return  -1
	
def ctrlToValue(name):
	""" Get the value of the controler name (-1==error). """
	
	try:
		return  upperCtrlNames.index(name.upper())
	except ValueError:
		return  -1
	
def valueToInst(val):
	""" Get the name of the inst. (or 'ERR'). """
	
	try:
		return  voiceNames[val]
	except IndexError:
		return "ERROR"


def valueToDrum(val):
	""" Get the name of the drum tone. (or 'ERR'). """

	try:
		return  drumNames[val-27]
	except IndexError:
		return "ERROR"

def valueToCtrl(val):
	""" Get the name of the controller (or 'ERR'). """
	
	try:
		return  ctrlNames[val]
	except IndexError:
		return "ERROR"

####################

def writeTracks(out):
	""" Write the accumulated MIDI tracks to file. """

	keys=gbl.mtrks.keys()
	keys.sort()
		
	if gbl.midiFileType == 0:
		trk0=gbl.mtrks[0].miditrk
		for n in keys[1:]:
			trk=gbl.mtrks[n].miditrk
			for k,v in trk.items():
				if k in trk0:
					trk0[k].extend(v)
				else:
					trk0[k]=v	

		keys=[0]

	out.write( mkHeader(len(keys), gbl.BperQ, gbl.midiFileType) )
	
	for n in keys:
		if len(gbl.mtrks[n].miditrk):
			gbl.mtrks[n].writeMidiTrack(out)	

			if gbl.debug:
				print "Writing <%s> ch=%s;" % \
					(gbl.mtrks[n].trackname, n),

	

""" MIDI number packing routines.
	
	These are necessary to create the MSB/LSB stuff that
	MIDI expects. All the routines use the Python chr()
	function way too much. A better/faster solution would be
	a C module.
	
"""


def intToWord(x):
	""" Convert INT to a 2 byte MSB LSB value. """
	
	return  chr(x>>8 & 0xff) + chr(x & 0xff)

def intTo3Byte(x):
	""" Convert INT to a 3 byte MSB...LSB value. """
	
	return intToLong(x)[1:]
		
def intToLong(x):
	""" Convert INT to a 4 byte MSB...LSB value. """
	
	return intToWord(x>>16) + intToWord(x)


def intToVarNumber(x): 
	""" Convert INT to a variable length MIDI value. """
	
	lst = chr(x & 0x7f)
	while  1:
		x = x >> 7
		if x:
			lst = chr((x & 0x7f) | 0x80) + lst
		else:
			return lst


def mkHeader(count, tempo, Mtype):

	return "MThd" + intToLong(6) + intToWord(Mtype) + \
		intToWord(count) + intToWord(tempo) 
	
	
""" Midi track class. All the midi creation is done here.
	
	We create a class instance for each track. mtrks{}.
"""

class Mtrk:

	def __init__(self, channel):
		self.miditrk={}
		self.channel = channel-1
		self.trackname = ''
		self.lastEvent = [None] * 129


	def delDup(self, offset, cmd):
		"""Delete a duplicate event. Used by timesig, etc.  """
		
		tr=self.miditrk
		lg=len(cmd)
		if tr.has_key(offset):
			for i,a in enumerate(tr[offset]):
				if a[0:lg] == cmd:
					del tr[offset][i]

				
	def addTimeSig(self, offset,  nn, dd, cc, bb):
		""" Create a midi time signature.
	
			delta - midi delta offset
			nn = sig numerator, beats per measure
			dd - sig denominator, 2=quarter note, 3=eighth, 
			cc - midi clocks/tick
			bb - # of 32nd notes in quarter (normally 8)
			
			This is only called by timeSig.set(). Don't
			call this directly since the timeSig.set() checks for
			duplicate settings.
		"""
		
		cmd = chr(0xff) + chr(0x58)
		self.delDup(offset, cmd)
		self.addToTrack(offset, cmd + chr(0x04) + \
			chr(nn) + chr(dd) + chr(cc) + chr(bb) )


	def addKeySig(self, offset, n):
		""" Set the midi key signature. """
		
		cmd = chr(0xff) + chr(0x59) 
		self.delDup(offset, cmd)
		self.addToTrack(offset, cmd + chr(0x02) + chr(n) + chr(0) )


	def addText(self, offset, msg):
		""" Create a midi TextEvent."""
	
		self.addToTrack( offset,
			chr(0xff) + chr(0x01) + intToVarNumber(len(msg)) + msg )


	def addLyric(self, offset, msg):
		""" Create a midi lyric event. """
		
		self.addToTrack( offset,
			chr(0xff) + chr(0x05) + intToVarNumber(len(msg)) + msg )
			
					
	def addTrkName(self, offset, msg):
		""" Creates a midi track name event. """
	
		if not self.trackname:
			self.trackname  = msg

		cmd = chr(0xff) + chr(0x03)
		self.delDup(offset, cmd)
		self.addToTrack(offset, cmd + intToVarNumber(len(msg)) + msg )
	
		
	def addProgChange( self, offset, program):
		""" Create a midi program change.
	
			program - midi program
		
			Returns - packed string
		"""

		self.addToTrack(offset,
			chr(0xc0 | self.channel) + chr(program) )


	def addGlis(self, offset, v):
		""" Set the portamento. LowLevel MIDI.
		
			This does 2 things:
				1. turns portamento on/off,
				2. sets the LSN rate.
		"""

		if v == 0:
			self.addToTrack(offset, 
				chr(0xb0 | self.channel) + chr(0x41) + chr(0x00) )

		else:
			self.addToTrack(offset,
				chr(0xb0 | self.channel) + chr(0x41) + chr(0x7f) )
			self.addToTrack(offset,
				chr(0xb0 | self.channel) + chr(0x05) + chr(v) )



	def addPan(self, offset, v):
		""" Set the lsb of the pan setting."""
		
		self.addToTrack(offset,
			chr(0xb0 | self.channel) + chr(0x0a) + chr(v) )


	def addCtl(self, offset, l):
		""" Add arbitary control sequence to track."""
		
		self.addToTrack(offset, chr(0xb0 | self.channel) + l)
		
			
	def addNoteOff(self, offset):
		""" Insert a "All Note Off" into the midi stream.
		
			Called from the cutTrack() function.
		"""

		self.addToTrack(offset, 
			chr(0xb0 | self.channel) + chr(0x7b) + chr(0) )
			
		
	def addChannelVol(self, offset, v):
		""" Set the midi channel volume."""
				
		self.addToTrack(offset,
			chr(0xb0 | self.channel) + chr(0x07) + chr(v) )


	def addTempo(self, offset, beats):
		""" Create a midi tempo meta event.
	
			beats - beats per second
	
			Return - packed midi string
		"""

		cmd = chr(0xff) + chr(0x51)
		self.delDup(offset, cmd)
		self.addToTrack( offset, cmd + chr(0x03) + intTo3Byte(60000000/beats) )


	def writeMidiTrack(self, out):
		""" Create/write the MIDI track.
		
			We convert timing offsets to midi-deltas.
		"""
		
		tr=self.miditrk
		
		if gbl.debug:
			ttl = 0
			lg=1
			for t in tr:
				a=len(tr[t])
				if a > lg:
					lg = a
				ttl += a
			print "Unique ts: %s; Ttl events %s; Average ev/ts %.2f" % \
				(len(tr), ttl,  float(ttl)/len(tr) )
				
		n = tr.keys()	# keys are offset times (deltas)
		n.sort()
		last = 0

		# Convert all events to MIDI deltas and store in
		# the track array/list

		tdata=[]		# empty track container
		lastSts=None    # Running status tracker
		
		for a in n:
			delta = a-last
			if delta < 0:	# random timings might create neg offsets?
				delta = 0
			for d in tr[a]:
				
				""" Running status check. For each packet compare
					the first byte with the first byte of the previous
					packet. If it is can be converted to running status
					we strip out byte 0. Note that valid running status
					byte are 0x80..0xef. 0xfx are system messages
					and are note suitable for running status.
				"""
				
				if len(d) > 1:
					if d[0] == lastSts:
						d=d[1:]
					else:
						lastSts = d[0]
						s=ord(lastSts)
						if s < 0x80 or s > 0xef or not gbl.runningStatus:  
							lastSts = None
							
				tdata.extend( [ intToVarNumber(delta) , d ] )
				delta = 0
			last = a

		# Add an EOF to the track (included in total track size)
		
		tdata.append( intToVarNumber(0))
		tdata.append( chr(0xff) + chr(0x2f) + chr(0x00) )
		
		tdata = ''.join(tdata)
		totsize = len(tdata)

		out.write("MTrk")
		out.write(intToLong(totsize))
		out.write( tdata )

	
	def addPairToTrack(self, boffset, startRnd, duration, note, v, unify):
		""" Add a note on/off pair to a track.
	
			boffset   - offset into current bar
			startRnd  - rand val start adjustment
			duration  - note len
			note      - midi value of note
			v         - midi velocity
			unify     - if set attempt to unify/compress on/offs
			
			This function tries its best to handle overlapping events.
			Easy to show effect with a table of note ON/OFF pairs. Both
			events are for the same note pitch.
			
				Offsets  |   200  |   300  |  320  |  420
				---------|--------|--------|-------|--------
				Pair1    |   on   |        |  off  |
				Pair2    |        |   on   |       |  off
				
			The logic here will delete the OFF event at 320 and
			insert a new OFF at 300. Result is that when playing
			Pair1 will turn off at 300 followed by the same note
			in Pair2 beginning sounded right after. Why the on/off?
			Remember: Velocities may be different!
			
			However, if the unify flag is set we should end up with:
			
				Offsets  |   200  |   300  |  320  |  420
				---------|--------|--------|-------|--------
				Pair1    |   on   |        |       |
				Pair2    |        |        |       |  off


		"""
	
		# Start/end offsets
		
		onOffset  = getOffset( boffset, startRnd)
		offOffset = onOffset + duration
		
		# ON/OFF events
		
		onEvent  = chr(0x90 | self.channel) + chr(note) + chr(v)
		offEvent = onEvent[:-1] + chr(0)
		
		""" Check for overlap on last event set for this track and
			do some ugly trickry.
			
			- The noOnFlag is set if we don't want to have the main
			  routine add in the ON event. This is set when UNIFY is
			  set and we have an overlap.
			  
			- We set F to the stored event time for this note and,
			  if it's in the same event range as the current event
			  we loop though the saved events for this track. We are
			  looking for a NOTE OFF event.
			  
			- If we get a matching event we then delete it from the
			  track. This requires 2 statements: one for an event
			  list with only 1 event, a 2nd for multiple events.
			  
			- If UNIFY is NOT set we insert a NOTE OFF at the current
			  on time. This replaces the OFF we just deleted.
			  
			- If UNIFY is SET we skip the above step, and we set the
			  noOnFlag so that the ON event isn't set.
			  
		"""

		noOnFlag = None
		
		f=self.lastEvent[note]
		if f >= onOffset and f <= offOffset:
			tr=self.miditrk
			for i in range(len(tr[f])):
				if tr[f][i] == offEvent:
					if len(tr[f]) == 1:
						del(tr[f])
					else:
						del(tr[f][i])
					if not unify:
						self.addToTrack(onOffset, offEvent)
					else:
						noOnFlag=1
					break

		if not noOnFlag:
			self.addToTrack(onOffset, onEvent )
		self.addToTrack(offOffset, offEvent )
		
		# Save the NOTE OFF time for the next loop.
		
		self.lastEvent[note] = offOffset
	
	
	def zapRangeTrack(self, start, end):
		""" Clear NoteOn events from track in range: start ... end.
			
			This is called from the fermata function.
			
			We delete the entire event list (3 bytes) from the buffer. This
			can result in empty directory enteries, but that isn't a problem.
		"""
	
		trk=self.miditrk	
		for a in trk:
			if a>=start and a<=end:
				for i in range(len(trk[a])-1, -1, -1):
					e = trk[a][i]
					if len(e)==3 and ord(e[0]) & 0xF0 == 0x90 and ord(e[2]):
						del trk[a][i]


	def addToTrack(self, offset, event):
		""" Add an event to a track.
	
			MIDI data is saved as created in track structures.
			Each track has a miditrk dictionary entry which used
			the time offsets and keys and has the various events
			as data. Each event is packed string of bytes and
			the events are stored as a list in the order they are
			created. Our storage looks like:
			
				miditrk[123] = [event1, event2, ...]
		"""
	
		if offset<0:
			offset=0
			
		tr=self.miditrk

		if offset in tr:
			tr[offset].append(event)
		else:
			tr[offset]=[event]

		
				

class TimeSig:

	def __init__(self):
		self.lastsig = (None,None)
		
	def set(self, nn, dd):
		if self.lastsig != (nn, dd):
			gbl.mtrks[0].addTimeSig(gbl.tickOffset, nn, dd, 48, 8)
			self.lastsig = (nn, dd)

	def get(self):
		return self.lastsig[:]


timeSig = TimeSig()



