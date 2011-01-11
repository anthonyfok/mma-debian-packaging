# MMAfile.py

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
	



import sys
import os
import MMAglobals;  gbl = MMAglobals
from MMAcommon import *

def locFile(name, lib):
	""" Locate a filename.
	
		This checks, in order:
			
			lib/name + .mma
			lib/name 
			name + .mma
			name
	"""

	ext=gbl.ext
	exists = os.path.exists
	
	if lib:
		if not name.endswith(ext):
			t="%s/%s%s" % (lib, name, ext)
			if exists(t):
				return t
		
		t="%s/%s" % (lib, name)
		if exists(t):
			return t

	if not name.endswith(ext):
		t = "%s%s" % (name, ext)
		if exists(t):
			return  t
	
	if exists(name):
		return name
			
	return None


###########################
# File read class
###########################


class ReadFile:

	class FileData:
		""" After reading the file in bulk it is parsed and stored in this
			data structure. Blanks lines and comments are removed.
		
		"""
	
		def __init__(self, lnum, data, label):
			self.lnum=lnum
			self.data=data
			self.label=label
	

	def __init__(self, fname):
	
		self.fdata=fdata=[]
		self.lastline = None
		self.lineptr = None
		self.fname = None
		self.lineno=0				
		
		self.que = []	# que for pushed lines (mainly for REPEAT)
		self.qnums = []
		
		self.beginData = []		# Current data set by a BEGIN statement
		self.beginPoints = []	# since BEGINs can be nested, we need ptrs
								# for backing out of BEGINs
	
		dataStore = self.FileData # shortcut to avoid '.'s
		
		try:
			inpath = file(fname, 'r')

		except:
			error("Unable to open '%s' for input" % fname)
			
		if gbl.debug or gbl.showFilenames:
			print "Opening file '%s'." % fname

		self.fname = fname
					
		""" Read entire file, line by line:

				- strip off blanks, comments
				- join continuation lines
				- parse out LABELS
				- create line numbers
		"""

		lcount=0
		label=''
		labs=[]		# track label defs, error if duplicate in same file

		while 1:
			l = inpath.readline()

			if not l:		# EOF
				break
				
			l= l.strip()
			lcount += 1

			if not l:
				continue
				
			while l[-1] == '\\':
				l = l[0:-1] + ' ' + inpath.readline().strip()
				lcount +=1
			
			
			""" This next line splits the line at the first found
				comment '//', drops the comment, and splits the
				remaining line into tokens using whitespace delimiters.
				Note that split() will strip off trailing and leading
				spaces, so a strip() is not needed here.
			"""
			
			l = l.split('//',1)[0].split()			

			if not l:			
				continue
				
		
			""" Parse out label lines. If a label is found we save
				it for the next loop. The line FOLLOWING the label
				line will have the label field in the storage set.
				Label lines are stripped out of the input.
			"""
			
			if l[0].upper()=='LABEL':
				if len(l) !=2:
					gbl.lineno = lcount
					error("Usage: LABEL <string>")
				label=l[1].upper()
				if label[0]=='$':
					gbl.lineno = lcount
					error("Variables are not permitted as labels")
				if label in labs:
					gbl.lineno = lcount
					error("Duplicate label specified in line %s." % lcount)
				labs.append(label)
				continue
				
			# Save the line, linenumber and (maybe) the label.

			fdata.append( dataStore(lcount, l, label))
			label=''
		
		inpath.close()

		self.lineptr = 0	
		self.lastline = len(fdata)	


	def toEof(self):
		""" Move pointer to End of File. """
		
		self.lineptr=self.lastline+1
		self.que = []
		self.qnums = []
		

	def goto(self, l):
		""" Do a goto jump.
		
			This isn't perfect, but is probably the way most GOTOs work. If
			inside a repeat/if then nothing more is processed. The jump is
			immediate. Of course, you'll run into problems with missing
			repeat/repeatend if you try it. Since all repeats are stacked
			back into the que, we just delete the que. Then we look for a
			matching label in the file line array.
			
			Label search is linear. Not too efficient, but the lists
			will probably never be that long either.
			
		"""
		
		if not l:
			error("No label specified")

		if self.que:
			self.que=[]
			
		fdata=self.fdata
		for p in range(self.lastline):
			if fdata[p].label==l:
				self.lineptr=p
				return
		
		error("Label '%s' has not be set." % l)
		
		
	def push(self, q, nums):
		""" Push a list of lines back into the input stream.
		
			Note: This is a list of semi-processed lines, no comments, etc.
		
			It's quicker to extend a list than to insert, so add to the end.
			Note: we reverse the original, extend() then reverse again, just
			in case the caller cares.
			
			nums is a list of linenumbers. Needed to report error lines.
		"""

		if not self.que:
			self.que = ['']
			self.qnums=[self.lineno]

		q.reverse()
		self.que.extend(q)
		q.reverse()

		nums.reverse()
		self.qnums.extend(nums)
		nums.reverse()
		
		
	def read(self):
		""" Return a line.
		
			This will return either a queued line or a line from the 
			file (which was stored/processed earlier).
		"""
		
		while 1:
				
			# Return a queued line if possible.
			
			if self.que:
				ln = self.que.pop(-1)

				self.lineno = self.qnums.pop()

				if not ln:
					continue

				return ln
		
			
			# Return the next line in the file.


			if self.lineptr>=self.lastline:
				if self.beginData:
					error("BEGIN active at EOF: %s" % ' '.join(self.beginData) )
					
				return None		####  EOF


			ln=self.fdata[self.lineptr].data
			self.lineno = self.fdata[self.lineptr].lnum
			self.lineptr +=1
			
			# Handle the BEGIN/END block stuff here
				
			if ln[0].upper() == 'BEGIN':
				ln = ln[1:]
				if not ln:
					error("Use: BEGIN STUFF.")

				self.beginPoints.append(len(self.beginData))
				self.beginData.extend(ln)
				continue

			if ln[0].upper()=='END':
				if len(ln) > 1:
					error("No arguments permitted for End")
					
				if not self.beginData:
					error("No 'Begin' for 'End'")
		
				self.beginData=self.beginData[:self.beginPoints.pop(-1)]
				continue

			if self.beginData:
				ln = self.beginData + ln


			
			return ln


