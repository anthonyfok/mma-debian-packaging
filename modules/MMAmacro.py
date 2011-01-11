
# MMAmacros.py

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
	
	The macros are stored, set and parsed in this single-instance
	class. At the top of MMAparse an instance in created with
	something like:  macros=MMMmacros.Macros().
"""

import MMAglobals;  gbl = MMAglobals
from MMAcommon import *

class Macros:

	vars={}         # storage
	expand = 1      # flag for variable expansion
		
	def __init__(self):
	
		self.vars={
			'_GROOVE':      '' ,
			'_LASTGROOVE':  '' ,
			'_TEMPO':       str(gbl.tempo) ,
			'_TRANSPOSE':   '0' ,
			'_TIME':        str(gbl.QperBar) ,
			'_SEQSIZE':     str(gbl.seqSize) }
			
		v = keyLookup(gbl.vols, gbl.volume)
		if not v:
			v = 'MF'
		self.vars['_VOLUME'] = v
		self.vars['_LASTVOLUME'] = v
		
	def expand(self, l):
		""" Loop though input line and make variable subsitutions.
			MMA variables are pretty simple ... any word starting 
			with a "$xxx" is a variable.
	
			l - list
		
			RETURNS: new list with all subs done.
		"""

		if not self.expand:
			return l
			
		while 1:
			sub=0
			for i,s in enumerate(l):
				if s[:2] == '$$':
					continue
				
				if s[0]=='$':
					s=s[1:].upper()
					if not s in self.vars:
						error("Variable '%s'  has not been defined." % s )

					ex=self.vars[s]
				
					if type(ex) == type([]):
						if len(ex) > 1:
							gbl.inpath.push( ex[1:], [gbl.lineno] * len(ex[1:]))
						if len(ex):
							ex=ex[0]
						else:
							ex=[]
					else:
						ex=ex.split()
					
					l=l[:i] + ex + l[i+1:]
					sub=1
					break
				
			if not sub:
				break

		return l


	def showvars(self, ln):
		""" Display all currently defined variables. """

		if len(ln):
			error("Use: Showvars. No argument permitted.")
				
		print "Variables defined:"
		kys = self.vars.keys()
		kys.sort()

		mx = 0
		for a in kys:			# get longest name
			if len(a) > mx:
				mx = len(a)
			
		mx = mx + 2
		for a in kys:
			print "  %-*s  %s" % (mx, '$'+a, self.vars[a])


	def setvar(self, ln):
		""" Set a variable """
	
	
		if len(ln) < 1:
			error("Use: SET VARIABLE_NAME [Value]")
			
		v=ln[0].upper()
		
		if v[0] in ('$','_'):
			error("Variable names cannot start with a '$' or '_'")
		
		self.vars[v]=" ".join(ln[1:])
		if gbl.debug:
			print "Variable $%s == '%s'" % (v, self.vars[v])		

	
	def msetvar(self, ln):
		""" Set a variable to a number of lines. """
	
		if len(ln) !=1:
			error("Use: MSET VARIABLE_NAME <lines> MsetEnd")
		v=ln[0].upper()
		
		if v[0] in ('$', '_'):
			error("Variable names cannot start with a '$' or '_'")
		
		lm=[]
		
		while 1:
			l=gbl.inpath.read()
			if not l:
				error("Reached EOF while looking for MSetEnd")
			cmd=l[0].upper()
			if cmd in ("MSETEND", 'ENDMSET'):
				if len(l) > 1:
					error("No arguments permitted for MSetEnd/EndMSet")
				else:
					break
			lm.append(l)

		self.vars[v]=lm
		

	def unsetvar(self, ln):
		""" Delete a variable reference. """

	
		if len(ln) != 1:
			error("Use: UNSET Variable")
		v=ln[0].upper()
		if v[0] == '_':
			error("Internal variables cannot be deleted or modified.")

		if v in self.vars:
			del(macros.vars[v])
			if gbl.debug:
				print "Variable '%s' UNSET" % v	
		else:
			warning("Attempt to UNSET nonexistent variable '%s'." % v)
	
			
	def vexpand(self, ln):

		if len(ln) == 1:
			cmd = ln[0].upper()
		else:
			cmd=''
			
		if cmd == 'ON':
			self.expand=1
			if gbl.debug:
				print "Variable expansion ON"		
		
		elif cmd == 'OFF':
			self.expand=0
			if gbl.debug:
				print "Variable expansion OFF"
		
		else:
			error("Use: Vexpand ON/Off.")


	def varinc(self, ln):
		""" Increment  a variable. """

		if len(ln) == 1:
			inc=1
		
		elif len(ln) == 2:
			inc = stof(ln[1], "Expecting a value (not %s) for Inc." % ln[1])

		else:
			error("Usage: INC Variable [value]")
		
		v=ln[0].upper()
	
		if v[0] == '_':
			error("Internal variables cannot be modified.")

		if not v in self.vars:
			error("Variable '%s' not defined")
			
		try:
			vl=int(self.vars[v])
		except:
			error("Variable must be a value to increment.")
			
		vl+=inc
		if vl == int(vl):
			vl = int(vl)
		self.vars[v]=str(vl)
		if gbl.debug:
			print "Variable '%s' INC to %s" % (v, self.vars[v])

	
	def vardec(self, ln):
		""" Decrement a varaiable. """

		if len(ln) == 1:
			dec = 1
					
		elif len(ln) == 2:
			dec = stof(ln[1], "Expecting a value (not %s) for Inc." % ln[1]) 

		else:
			error("Usage: DEC Variable [value]")
		
		v=ln[0].upper()
		if v[0] == '_':
			error("Internal variables cannot be modified.")

		if not v in self.vars:
			error("Variable '%s' not defined")
			
		try:
			vl=int(self.vars[v])
		except:
			error("Variable must be a value to decrement.")
			
		vl-=dec
		if vl == int(vl):
			vl = int(vl)

		self.vars[v]=str(vl)
		if gbl.debug:
			print "Variable '%s' DEC to %s" % (v, self.vars[v])

		
	def varIF(self, ln):	
		""" Conditional variable if/then. """

		def expandV(l):
			""" Private func. """
			
			l=l.upper()

			if l[:2] == '$$':
				l=l[2:]
				if not l in self.vars:
					error("String Variable '%s' does not exist." % l)
				l=self.vars[l]
			
			try:
				v=float(l)
			except:
				v=None
					
			return ( l, v )
	
	
		def readblk():
			""" Private, reads a block until ENDIF, IFEND or ELSE.
				Return (Terminator, lines[], linenumbers[] )
			"""
		
			q=[]
			qnum=[]
			nesting=0		
		
			while 1:
				l=gbl.inpath.read()
				gbl.lineno = gbl.inpath.lineno
				if not l:
					error("EOF reached while looking for EndIf")

				cmd=l[0].upper()
				if cmd == 'IF':
					nesting+=1
				if cmd in ("IFEND", 'ENDIF', 'ELSE'):
					if len(l) > 1:
						error("No arguments permitted for IfEnd/EndIf/Else")
					if not nesting:
						break
					if cmd != 'ELSE':
						nesting -= 1
			
				q.append(l)
				qnum.append(gbl.inpath.lineno)
		
			return (cmd, q, qnum)

	
		if len(ln)<2:
			error("Usage: IF <Operator> ")
			
		action = ln[0].upper()
			
		# 1. do the unary options: DEF, NDEF
	
		if action in ('DEF', 'NDEF'):
			if len(ln) != 2:
				error("Usage: IF %s VariableName" % action)
			
			v=ln[1].upper()
			retpoint = 2
		
			if action == 'DEF':
				compare = self.vars.has_key(v)
			elif action == 'NDEF':
				compare = ( not self.vars.has_key(v))
			else:
				error("Unreachable unary conditional")
		
			
		# 2. Binary ops: EQ, NE, etc.

		elif action in ('LT', 'LE', 'EQ', 'GE', 'GT', 'NE'):
			if len(ln) != 3:
				error("Usage: VARS %s Value1 Value2" % action)

			
			s1,v1 = expandV(ln[1])
			s2,v2 = expandV(ln[2])

			if type(v1) == type(1.0) and type(v2) == type(1.0):
				s1=v1
				s2=v2
			
		
			retpoint = 3			

			if   action == 'LT':
				compare = (v1 <  v2)	
			elif action == 'LE':
				compare = (v1 <= v2)
			elif action == 'EQ':
				compare = (v1 == v2) 
			elif action == 'GE':
				compare = (v1 >= v2) 
			elif action == 'GT':
				compare = (v1 >  v2) 
			elif action == 'NE':
				compare = (v1 != v2) 
			else:
				error("Unreachable binary conditional")
		
		else:
			error("Usage: IF <CONDITON> ...")
		

		""" Go read until end of if block.
			We shove the block back if the compare was true.
			Unless, the block is terminated by an ELSE ... then we need
			to read another block and push back one of the two.
		"""
	
		cmd, q, qnum = readblk()
	
				
		if cmd == 'ELSE':
			cmd, q1, qnum1 = readblk()
		
			if cmd == 'ELSE':
				error("Only one ELSE is permitted in IF construct.")
			
			if not compare:
				compare = 1
				q = q1
				qnum = qnum1

		if compare:
			gbl.inpath.push( q, qnum )
		

macros = Macros()
