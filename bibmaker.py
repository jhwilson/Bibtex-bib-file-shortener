#! /usr/bin/env python

# This file looks in a supplied .tex file for any citations made that
# are located in some unchanging .bib file (specified by
# MASTERBIBLIOGRAPHYPATH below), and creates a new, local, .bib file
# with only those references used in the .tex file.

# This file takes three arguments, the last two are optional
#
# $./bibmaker TEXFILE NEWBIBFILENAME MASTERBIBFILE
#
# If NEWBIBFILENAME isn't specified, it will default to "references".
#   - TEXFILE: The name of the .tex file to find the citations in -
#   - NEWBIBFILENAME: The name to be given to the new .bib file -
#   - MASTERBIBFILE: If provided, this will override the internal
#       default master bibliography file with a new one of the user's
#       choosing

######################################################################
# This it the (default) path to the master bibliography file to be
# used.

MASTERBIBLIOGRAPHYPATH = "~/texmf/bibtex/bib/my_bib/master.bib"

######################################################################

import sys
import re
import os

bibext = re.compile("\.bib")
texext = re.compile("\.tex")
if sys.argv[1]:
    filename = texext.sub("",sys.argv[1])+".tex"
else:
    print "ERROR: NO FILENAME SPECIFIED"
if len(sys.argv) >= 3:
    bibliographyname = bibext.sub("",sys.argv[2])
else:
    bibliographyname = "references"
if len(sys.argv) >= 4:
    masterpath = bibext.sub("",sys.argv[3])+".bib"
else:
    masterpath = MASTERBIBLIOGRAPHYPATH
masterpath = masterpath.replace("~",os.getenv("HOME"))

texfile = open(filename,"r")
filebuffer = texfile.read()
texfile.close()
REcitation = re.compile(r"\\cite\{[^\}]*\}")
RETeXcite = re.compile(r"\\cite")
REinclusion = re.compile(r"\\include\{[^\}]*\}")
citations = REcitation.findall(filebuffer)
inclusions = REinclusion.findall(filebuffer)
REmastername = re.compile(r"[^/]+\.bib")
mastergroup = REmastername.search(masterpath)
mastername = bibext.sub("",mastergroup.group())

filebuffer = re.sub(r"\\bibliography\{[\s]*"+mastername+"[\.bi]*[\s]*\}","\\bibliography{"+bibliographyname+"}",filebuffer)
filebuffer = filebuffer.replace("\x08ibliography","\\bibliography")
texfile = open(filename,"w")
texfile.write(filebuffer)
texfile.close()

includedfiles = []
for aninclusion in inclusions:
    aninclusion = re.sub(r"\\include\{[\s]*","",aninclusion)
    aninclusion = re.sub(r"[\s]*\}","",aninclusion)
    includedfiles = includedfiles + [re.sub("\.tex","",aninclusion)]
for afile in includedfiles:
    texfile = open(afile+".tex","r")
    citations = citations + REcitation.findall(texfile.read())
    texfile.close()

labels = []
for acitation in citations:
    acitation = RETeXcite.sub("",acitation)
    labels = labels + re.split("[\s,\{\}]+",acitation)
labels = list(set(labels))
if labels[0] == "":
    labels = labels[1:]

masterbib = open(masterpath,"r")
referencebib = open(bibliographyname+".bib","w")
for alabel in labels:
    bibitemregxp = "@[a-zA-Z]+\{[\s]*" + alabel + "[\s]*,"
    REbibitem = re.compile(bibitemregxp)
    bibitem = REbibitem.search(masterbib.read())
    if bibitem:
        masterbib.seek(bibitem.end())
        openbraces = 1
        iterations = 0
        while openbraces != 0:
            char = masterbib.read(1)
            iterations = iterations + 1
            if char == "{":
                openbraces = openbraces + 1
            elif char == "}":
                openbraces = openbraces - 1
        masterbib.seek(bibitem.start())
        entirebibitem = masterbib.read(bibitem.end()-bibitem.start()+iterations)
        referencebib.write(entirebibitem+"\n")
    else:
        print "Did not find the citation in bibliography:", alabel        
    masterbib.seek(0)
masterbib.close()

print "New bibliography file:", bibliographyname+".bib", "created."
print "LaTeX file", filename, "modified to use new bibliography."
