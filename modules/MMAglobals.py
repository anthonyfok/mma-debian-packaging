# MMAglobals.py

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
	



import os

version = "0.12"		# current program version


""" mtrks is storage for the MIDI data as it is created.
	It is a dict of class Mtrk() instances. Keys are the
	midi channel numbers. Ie, mtrks[2] 	is for channel 2,
	etc. mtrks[0] is for the meta stuff. 
"""
	
mtrks = {}

"""	tnames is a dict of assigned track names. The keys are
	the track names; each entry is a pattern class instance. 
	We have tnames['BASS-FOO'], etc.
"""

tnames = {}

"""	midiAssigns keeps track of channel/track assignments. The keys
	are midi channels (1..16), the data is a list of tracks assigned
	to each channel. The tracks are only added, not deleted. Right
	now this is only used in -c reporting.
"""
	
midiAssigns={}
for c in range(0,17):
	midiAssigns[c]=[]

""" midiAvail is a list with each entry representing a MIDI channel.
	As channels are allocated/deallocated the appropriated slot
	is inc/decremented.
"""

midiAvail=[ 0 ] * 17   # slots 0..16, slot 0 is not used.

deletedTracks = []	# list of deleted tracks for -c report

""" This is a user constructed list of names/channels. The keys
	are names, data is a channel. Eg. midiChPrefs['BASS-SUS']==9
"""

midiChPrefs={}

""" String constants """

ext = ".mma"		# extension for song/lib files.

""" Volumes are specified in musical terms, but converted to
	midi velocities. This table has a list of percentage changes
	to apply to the current volume. Used in both track and global
	situations. Note that the volume for 'ffff' is 150%--this will
	most likely generate velocities outside the midi range of 0..127.
	But that's fine since mma will adjust volumes into the valid
	range. Using very high percentages will ensure that 'ffff' notes
	are (most likely) sounded with a maximum velocity.
"""

vols={	'OFF':	0,		'PPPP': 20,		'PPP':	30,
		'PP':	45,		'P':	55,		'MP':	75,
		'MF':	90,		'F':	100,	'FF':	110,
		'FFF':	120,	'FFFF':	150		}

volume = vols['MF']		# default global volume


"""	Tempo, and other midi positioning. """

BperQ      =  192   # midi ticks per quarter note
QperBar    =  4     # Beats/bar, set with TIME
tickOffset =  0     # offset of current bar in ticks
tempo      =  120   # current tempo
seqSize    =  1     # variation sequence table size
seqCount   =  0     # running count of variation

transpose  =  0     # Transpose is global (ignored by drum tracks)

keySig     = ['',0] # only used in solo tracks

lineno     = -1     # used for error reporting

""" Path and search variables. """

libPath = ''
for  p in ("/usr/local/share/mma/lib",
			"/usr/share/mma/lib",
			"./lib"):
	if os.path.isdir(p):
		libPath=p
		break
		
incPath = ''
for p in ("/usr/local/share/mma/includes",
			"/usr/share/mma/includes",
			"./includes"):
	if os.path.isdir(p):
		incPath=p
		break		

outPath    =   ''     # Directory for MIDI file
mmaStart   =   []     # list of START files
mmaEnd     =   []     # list of END files
inpath     =   None   # input file

midiFileType    = 1      # type 1 file, SMF command can change to 0
runningStatus =  1      # running status enabled

"""	List of defined grooves. Used by auto to track
	known grooves.
"""

mkGrooveList = []

""" Storage for grooves and volumes. Note, the per-track settings
	are saved in the track pattern classes. In both, the keys are
	the groove/volgroove names and the data is a list of settings.
"""

settingsGroove  = {}
volumeGroove    = {}


""" These variables are all set from the command line in MMAopts.py.
	It's a bit of easy-way-out to have them all here, but I don't think
	it hurts too much.
"""

debug         =  0
pshow         =  0
seqshow       =  0
showrun       =  0
noWarn        =  0
noOutput      =  0
showExpand    =  0
showFilenames =  0
chshow        =  0
outfile       =  None
infile        =  None
docs          =  0
maxBars       =  500
makeGrvDefs   =  0
cmdSMF          = None


