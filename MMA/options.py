# options.py

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

Bob van der Poel <bob@mellowood.ca>

"""

import getopt
import sys
import os

import MMA.docs
import MMA.parse
import MMA.chords
import MMA.alloc
import MMA.volume
import MMA.exits

import gbl
from   MMA.common import *
from   MMA.macro  import macros

def opts():
    """ Option parser. """

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
            "b:B:dpsS:ri:wneom:f:M:cgGvVD:01PT:", [] )
    except getopt.GetoptError:
        usage()

    for o,a in opts:

        if  o == '-b':
            setBarRange(a)

        elif o == '-B':
            setBarRange(a)
            gbl.barRange.append("ABS")
        
        elif o == '-d':
            gbl.debug = gbl.Ldebug = 1

        elif o == '-o':
            gbl.showFilenames = gbl.LshowFilenames = 1

        elif o == '-p':
            gbl.pshow = gbl.Lpshow = 1

        elif o == '-s':
            gbl.seqshow = gbl.Lseqshow = 1

        elif o == '-S':
            ln = a.split('=', 1)
            macros.setvar(ln)

        elif o == '-r':
            gbl.showrun = gbl.Lshowrun = 1

        elif o == '-w':
            gbl.noWarn = gbl.LnoWarn = 1

        elif o == '-n':
            gbl.noOutput = gbl.LnoOutput = 1

        elif o == '-e':
            gbl.showExpand = gbl.LshowExpand = 1

        elif o == '-c':
            gbl.chshow = gbl.Lchshow = 1

        elif o == '-f':
            gbl.outfile = a

        elif o == '-i':
            gbl.mmaRC = a

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
                error("Only a '0' or '1' is permitted for the -M arg")

        elif o == '-T':   # set tracks to generate, mute all others
            gbl.muteTracks = a.upper().split(',')
            

        elif o == '-D':
            if a == 'xl':
                gbl.createDocs = 1

            elif a == 'xh':
                gbl.createDocs = 2

            elif a == 's':
                gbl.createDocs = 3

            elif a == 'gh':
                gbl.createDocs = 4

            elif a == 'bo':
                gbl.createDocs = 99

            elif a == 'k':

                def pl(msg, lst, adds):
                    print msg,
                    for i in sorted(lst.keys() + adds):
                        print i,
                    print "\n"

                pl("Base track names:", MMA.alloc.trkClasses, [])
                pl("Commands:", MMA.parse.simpleFuncs,
                   ["BEGIN", "END",] )
                pl("TrackCommands:", MMA.parse.trackFuncs, [])
                print "Not complete ... subcommands, comments, chords..."
                sys.exit(0)

            else:
                print "Unknown -D option."
                usage()

        elif o == '-0':
            gbl.synctick = 1

        elif o == '-1':
            gbl.endsync = 1

        elif o == '-P':
            gbl.playFile = 1

        elif o == '-V':
            gbl.playFile = 2  # signal create and play groove
            if not args: 
                error("-V: option requires Groove Name.")
        
            tfile = "MMAtmp%s.mma" % os.getpid()
            op = open( tfile, "w")
            groove=''
            cmds=[]
            chords="I, vi, ii, V7"
            count=4
            for g in args:
                if '=' in g:
                    c=g.split('=')
                    if c[0].upper() == 'CHORDS':
                        chords = c[1]
                    elif c[0].upper() == "COUNT":
                        count = c[1]
                        try:
                            count=int(count)
                        except:
                            error("-V: expecting integer for Count.")
                    else:
                        cmds.append(c)
                elif groove:
                    error( "-V: Only one groove name permitted.")
                else:
                    groove=g
            if not groove:
                error("-V: no groove name specified.")
                          
            op.write("Groove %s\n" % groove)
            for g in cmds:
                op.write("%s %s \n" % (g[0], g[1]))
            chords = chords.split(',')
            while len(chords) < count:
                chords += chords
            chords = chords[:count]
            for c in chords:
                op.write("%s\n" % c)

            op.close()
        
            MMA.exits.files.append(tfile)

            args = [tfile]

        else:
            usage()      # unreachable??


    # we have processed all the args. Should just have a filename left

    if len(args)>1:
        usage("Only one input filename is permitted, %s given on command line." % len(args) )

    if gbl.infile:
        usage("Input filename already assigned ... should not happen.")

    if args:
        gbl.infile = args[0]

             

def usage(msg=''):
    """ Usage message. """
    
    txt=[
        "MMA - Musical Midi Accompaniment",
        "  Copyright 2003-11, Bob van der Poel. Version %s" % gbl.version ,
        "  Distributed under the terms of the GNU Public License.",
        "  Usage: mma [opts ...] INFILE [opts ...]",
        "",
        "Options:",
        " -b <n> Limit compilation to n1-n2 bars (comment numbers)",
        " -B <n> Like -b but for absolute bar numbers",
        " -c    display default Channel assignments",
        " -d    enable lots of Debugging messages",
        " -Dk   print list of MMA keywords",
        " -Dxl  eXtract Latex doc blocks from file",
        " -Dxh  eXtract HTML doc blocks from file",
        " -Dgh  extract HTML Groove doc",
        " -Dbo  extract text for browser app",
        " -Ds   extract sequence lists from file",
        " -e    show parsed/Expanded lines",
        " -f <file>  set output Filename",
        " -g    update Groove dependency database",
        " -G    create Groove dependency database",
        " -i <file> specify init (mmarc) file",
        " -m <x> set Maxbars (default == 500)",
        " -M <x> set SMF to 0 or 1",
        " -n    No generation of midi output",
        " -o    show complete filenames when Opened",
        " -p    display Patterns as they are defined",
        " -P    play song (don't save) with player",
        " -r    display Running progress",
        " -s    display Sequence info during run",
        " -S <var[=data]>  Set macro 'var' to 'data'",
        " -T <tracks> Limit generation to specified tracks",
        " -v    display Version number",
        " -V <groove [options]> preview play groove",
        " -w    disable Warning messages",
        " -0    create sync at start of all channel tracks",
        " -1    create sync at end of all channel tracks" ]


    for a in txt:
        print a

    if msg:
        print
        print msg

    print
    sys.exit(1)



def setBarRange(v):
    """ Set a range of bars to compile. This is the -B/b option."""

    if gbl.barRange:
        error("Only one -b or -B permitted.")

    for ll in v.split(','):

        l = ll.split("-")

        if len(l) == 2:
            s,e = l
            try:
                s = int(s)
                e = int(e)
            except:
                usage("-B/b ranges must be integers, not '%s'." % l)

            for a in range(s,e+1):
                gbl.barRange.append(str(a))

        elif len(l) == 1:
            try:
                s=int(l[0])
            except:
                usage("-B/b range must be an integer, not '%s'." % l[0])
            gbl.barRange.append(str(s))

        else:
            usage("-B/b option expecting N1-N2,N3... not '%s'." % v)



