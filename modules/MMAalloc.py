
# MMAalloc.py

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
	


import MMApatChord
import MMApatWalk
import MMApatBass
import MMApatDrum
import MMApatScale
import MMApatArpeggio
import MMApatSolo

import MMAglobals;  gbl = MMAglobals

from MMAcommon import *

def trackAlloc(name, err):
	""" Check existence of track and create if possible.

		Needs to be in this module so we can determine the different
		class names (they are not known anywhere else).
			
		If 'err' is set, the function will 'error out' if
		it's not possible to create the track. Otherwise,
		it is content to return without creation taking place.
	"""

	# If the track already exists, just return
	
	if name in gbl.tnames:
		return 

	trackClass = None
	ext = None
	base = name

	""" Loop though the valid track names. We're trying to
		get the TYPE from the name. The name can be either
			1. The name of the base track (ie: BASS)
			2. Base track plus a '-' and string (ie: BASS-SUS)
	"""
		
	if name.count('-'):
		base, ext = name.split('-',1)


	for f,n in (
			(MMApatBass.Bass,          'BASS'     ), 
			(MMApatChord.Chord,        'CHORD'    ),
			(MMApatArpeggio.Arpeggio,  'ARPEGGIO' ),
			(MMApatScale.Scale,        'SCALE'    ),
			(MMApatDrum.Drum,          'DRUM'     ),
			(MMApatWalk.Walk,          'WALK'     ),
			(MMApatSolo.Melody,        'MELODY'   ),
			(MMApatSolo.Solo,          'SOLO'     )
				):

		if base == n:
			trackClass = f
			break
			
	
	""" If we did not set 'trackClass' then the name is not valid 
		and we obviously can't create the track. Error out or return...
	"""
		
	if not trackClass:
		if err:
			error("There is no track class '%s' for trackname '%s'" % \
				(base, name))
		else:
			return
	

	# Now attempt to allocate the track
	
	gbl.tnames[name]=f(name)
	newtk=gbl.tnames[name]

	# Update current grooves to reflect new track.
	
	for slot in gbl.settingsGroove.keys():
		newtk.saveGroove(slot)					

	# Set the sequence size of new track
	
	newtk.setSeqSize()


	if gbl.debug:
		print "Creating new track", name

	return 
	


