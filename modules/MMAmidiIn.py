
# MMAimport.py

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

import MMAmidi
from MMAalloc import trackAlloc
import MMAglobals;  gbl = MMAglobals
from MMAcommon import *

# The following 2 variables are global. A bit ugly :)

midifile = ''	# The imported MIDI file as a long string
offset = 0		# Current pointer into the MIDI file

# Convert MIDI variables to integers.

def mvarlen():
	""" Convert variable length midi value to int. """

	global offset
		
	x=0L
	for i in range(4):

		try:
			byte=ord(midifile[offset])
			offset += 1
		except:
			error("Invalid MIDI file include (varlen->int).")
			
		if byte < 0x80:
			x = ( x << 7 ) + byte
			break
		else:
			x = ( x << 7 ) + ( byte & 0x7f )

	return int(x)

def chars(count):
	""" Return 'count' chars from file. """
	
	global offset
	
	bytes=midifile[offset:offset+count]
	offset+=count
	return bytes
	
def m1i():
	""" Get 1 byte. """
	
	global offset
	
	try:
		byte = midifile[offset]
		offset += 1
	except:
		error("Invalid MIDI file include (byte, offset=%s)." % offset)
	
	return ord(byte)
	
		
def m32i():
	""" Convert 4 bytes to integer """
	
	global offset
	
	x = 0L
	for i in range(4):
		try:
			byte = midifile[offset]
			offset += 1
		except:
			error("Invalid MIDI file include (i32->int, offset=%s)." % offset)
		x = (x << 8) + ord(byte)

	return int(x)

def m16i():
	""" Convert 2 bytes to integer """
	
	global offset
	
	x = 0L
	for i in range(2):
		try:
			byte = midifile[offset]
			offset += 1
		except:
			error("Invalid MIDI file include (i16->int, offset=%s)." % offset)
		x = (x << 8) + ord(byte)
		
	return int(x)


######################################################


def midiinc(ln):
	""" Include a MIDI file into MMA generated files. """
	
	global midifile, offset
	
	filename = ''
	volAdjust = 100
	octAdjust = 0
	transpose = None
	channels = []
	
	for a in ln:
		cmd, opt = a.split('=')
		
		cmd=cmd.upper()
		
		if cmd == 'FILE':
			filename = opt
			
		elif cmd == 'VOLUME':
			volAdjust = stoi(opt)
			
		elif cmd == 'OCTAVE':
			octAdjust = stoi(opt)
			if octAdjust < -4 or octAdjust > 4:
				error("Octave adjustment must be -4 to 4, not %s." % opt)
			octAdjust *= 12
		
		elif cmd == 'TRANSPOSE':
			transpose = stoi(opt)
			if transpose < -24 or transpose > 24:
				error("Tranpose must be -24 to 24, not %s." % opt)

		# make sure this is last option
		
		else:
			trackAlloc(cmd, 0)
			if not cmd in gbl.tnames:
				error("%s is not a valid MMA track." % cmd)
			
			ch = stoi(opt)
			if ch < 1 or ch > 16:
				error("MIDI channel for import must be 1..16, not %s." % ch)
				
			channels.append( (cmd, ch-1))
			


	# If transpose was NOT set, use the global transpose value
	
	if transpose == None:
		transpose = gbl.transpose
	
	octAdjust += transpose	# this takes care of octave and transpose
			
	try:
		inpath = file(filename, "rb")
	except:
		error("Unable to open MIDI file %s for reading" % filename)

	midifile=inpath.read()
	inpath.close()

	# Create our storage. This is a dic with keys=channels
	
	events={}
	for c in range(0,16):
		events[c]=[]
		
	# Ensure this is valid header
	
	hd=midifile[0:4]
	if hd != 'MThd':
		error("Expecting 'HThd', %s not a standard midi file." % filename)

	offset = 4	
	a = m32i()

	if a != 6:
		error("Expecting a 32 bit value of 6 in header")

	format=m16i()
	
	if format not in (0,1):
		error("MIDI file format %s not recognized" % format)
	
	ntracks=m16i()
	beatDivision=m16i()
	
	if beatDivision != gbl.BperQ:
		warning("MIDI file '%s' tick/beat of %s differs from MMA's "
			"%s. Will try to compensate." % 
			(filename, beatDivision, gbl.BperQ))

	midievents={}
	firstNote = 0xffffff
	
	for tr in range(ntracks):
		tm=0
				
		hdr = midifile[offset:offset+4]
		offset+=4

		if hdr != 'MTrk':
			error("Malformed MIDI file in track header")
		trlen = m32i()	# track length, not used?
		
		lastevent = None
		while 1:
			tm += mvarlen()		# adjust total offset by delta

			ev=m1i()
			
			if ev < 0x80:
				if not lastevent:
					error("Illegal running status in %s at %s" \
						% (midifile, offset))
				offset -= 1
				ev=lastevent
			
					
			sValue = ev>>4		# Shift MSBs to get a 4 bit value
			channel = ev & 0x0f
			
			if sValue == 0x8:		# note off event

				note=m1i()
				vel=m1i()

				if octAdjust and channel != 10:
					note += octAdjust
					if note < 0 or note > 127:
						continue


				events[channel].append([tm, ev & 0xf0, chr(note)+chr(vel)])
		
			elif sValue == 0x9:		# note on event
				if tm < firstNote:
					firstNote = tm
				
				note=m1i()
				vel=m1i()
				
				if octAdjust and channel != 10:
					note += octAdjust
					if note < 0 or note > 127:
						continue

				if volAdjust != 100:
					vel = int( (vel*volAdjust)/100)
					if vel<0: vel=1
					if vel>127: vel=127
				
				events[ev & 0xf].append([tm, ev & 0xf0,  chr(note)+chr(vel)])
	
			elif sValue == 0xa:		# key pressure
				events[ev & 0xf].append([tm, ev & 0xf0, char(2)])

			elif sValue == 0xb:		# control change
				events[ev & 0xf].append([tm, ev & 0xf0, chars(2)])
	
			elif sValue == 0xc:		# program change
				events[ev & 0xf].append([tm, ev & 0xf0, char(1)])
	
			elif sValue == 0xd:		# channel pressure
				events[ev & 0xf].append([tm, ev & 0xf0, char(1)])
	
			elif sValue == 0xe:		# pitch blend
				events[ev & 0xf].append([tm, ev & 0xf0, chars(2)])
	
			elif sValue == 0xf:		# system, all ignored
				if ev == 0xff:		# meta events
					a=m1i()
			
					if a == 0x00:	# sequence number
						l=mvarlen()
						offset += l
			
					elif a == 0x01:	# text
						l=mvarlen()
						offset += l

					elif a == 0x02:	# copyright
						l=mvarlen()
						offset += l
				
					elif a == 0x03:	# seq/track name
						l=mvarlen()
						offset += l
				
					elif a == 0x04:	# instrument name
						l=mvarlen()
						offset += l
				
					elif a == 0x05:	# lyric
						l=mvarlen()
						offset += l
				
					elif a == 0x06:	# marker
						l=mvarlen()
						offset += l
				
					elif a == 0x07:	# cue point
						l=mvarlen()
						offset += l
			
					elif a == 0x21:	# midi port
						l=mvarlen()
						offset += l
				
					elif a == 0x2f:	# end of track
						l=mvarlen()
						offset += l
						break
										
					elif a == 0x51:	#tempo
						l=mvarlen()
						offset += l

					elif a == 0x54:	# SMPTE offset
						l=mvarlen()
						offset += l
				
					elif a == 0x58:	# time sig
						l=mvarlen()
						offset += l
				
					elif a == 0x59:	# key sig
						l=mvarlen()
						offset += l

					else:		# probably 0x7f, proprietary event
						l=mvarlen()
						offset += l

				
				elif ev == 0xf0:	# system exclusive
					l=mvarlen()
					offset += l
			
				elif ev == 0xf2:	# song position pointer, 2 bytes
					offset += 2
			
				elif ev == 0xf3:	# song select, 1 byte
					offset += 1
	
				else:		# all others are single byte commands
					pass

			if ev >= 0x80 and ev <= 0xef:
				lastevent = ev
					
	
	# Midi file parsed, add selected events to mma data
	
	beatad = gbl.BperQ / float(beatDivision)
	
	for tr, ch in channels:
		t=gbl.tnames[tr]
		if not t.channel:
			t.setChannel()

		t.clearPending()
		if t.voice[0] != t.ssvoice:
			gbl.mtrks[t.channel].addProgChange( gbl.tickOffset,  t.voice[0])

		channel = t.channel
		track = gbl.mtrks[channel]

		for ev in events[ch]:
			
			track.addToTrack( gbl.tickOffset + int((ev[0]-firstNote) * beatad), 
				chr(ev[1] | channel-1) + ev[2] )


