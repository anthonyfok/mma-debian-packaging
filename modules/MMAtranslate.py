
# MMAtranslate.py

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


	This module handles voice name translations.	
"""

import MMAglobals;  gbl = MMAglobals

class Vtable:

	def __init__(self):
		self.table = {}
				
	def set(self, ln):
		""" Set a name/alias for voice translation, called from parser. """

		if not ln:
			self.table = {}
			if gbl.debug:
				print "Voice Translaion table reset."	

			return
				
		for l in ln:
			l=l.upper()
			if l.count('=') != 1:
				error("Each translation pair must be in the format Voice=Alias")
			v,a = l.split('=')
			self.table[v] = a
		
		if gbl.debug:
			print "Voice Translations: ",
			for l in ln:
				print l,
			print
	
	def get(self, name):
		""" Return a translation or original. """
			
		name=name.upper()
		if self.table.has_key(name):
			return self.table[name]
		
		else:
			return name
		

vtable=Vtable()			# Create single class instance. 


