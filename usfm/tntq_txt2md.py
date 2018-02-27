# coding: latin-1
# This script converts a repository of tN or tQ text files from tStudio to .md format.
#    Parses directory names to get the book IDs
#    Specify target output folder.
#    Standardizes the names of book folders in the target folder.
#    Converts multiple books at once.
#    Makes a manifest.txt file to be pasted into manifest.yaml.
# This script doesn't do anything if the files are .md files already.

# Global variables
target_dir = r'C:\Users\Larry\Documents\GitHub\Kannada\kn_tn.temp'
verseCounts = {}

import re
import io
import os
import sys
import json

# Parses the specified folder name to extract the book ID.
# These folder names are generated by tStudio in the form: language_book_tn.
# Return upper case bookId or empty string if failed to retrieve.
def getBookId(folder):
    bookId = ""
    parts = folder.split('_')
    if len(parts) == 3:
        bookId = parts[1]
    elif len(parts) == 1 and len(folder) == 3:
        bookId = folder
    return bookId.upper()

# Returns the English book name from verses.json
def getBookTitle(id):
    title = ""
    if id:
        loadVerseCounts()
        title = verseCounts[id]['en_name']
    return title

def appendToManifest(bookfolder, bookId, bookTitle):
    path = makeManifestPath()
    manifest = io.open(path, "ta", buffering=1, encoding='utf-8', newline='\n')
    manifest.write(u"  -\n")
    title = bookTitle + u" translationNotes"
    if bookfolder[-1:].upper() == 'Q':
        title = bookTitle + u" translationQuestions"
    manifest.write(u"    title: '" + title + u"'\n")
    manifest.write(u"    versification: ''\n")
    manifest.write(u"    identifier: '" + bookId.lower() + u"'\n")
    manifest.write(u"    sort: 0\n")
    manifest.write(u"    path: './" + bookId + u"'\n")
    manifest.write(u"    categories: []\n")
    manifest.close()

# Opens the verses.json file, which must reside in the same path as this .py script.
def loadVerseCounts():
    global verseCounts
    if len(verseCounts) == 0:
        jsonPath = os.path.dirname(os.path.abspath(__file__)) + "\\" + "verses.json"
        if os.access(jsonPath, os.F_OK):
            f = open(jsonPath, 'r')
            verseCounts = json.load(f)
            f.close()
        else:
            sys.stderr.write("File not found: verses.json\n")

# Returns path of temporary manifest file block listing projects converted
def makeManifestPath():
    return os.path.join(target_dir, "manifest.txt")
    
def makeMdPath(id, chap, chunk):
    mdPath = os.path.join(target_dir, id)
    if not os.path.isdir(mdPath):
        os.mkdir(mdPath)

    mdPath = os.path.join(mdPath, chap)
    if not os.path.isdir(mdPath):
        os.mkdir(mdPath)

    return os.path.join(mdPath, chunk[0:2]) + ".md"

# Returns True if the specified file name matches a pattern that indicates
# the file contains text to be converted.
def isChunk(filename):
    isSect = False
    if re.match('\d\d\.txt', filename) and filename != '00.txt':
        isSect = True;
    return isSect

# Returns True if the specified directory is one with text files to be converted
def isChapter(dirname):
    isChap = False
    if len(dirname) == 2 and dirname != '00' and re.match('\d\d', dirname):
        isChap = True
    return isChap

# Converts .txt file in fullpath location to .md file in target dir.
def convertFile(id, chap, fname, fullpath):
    # Open output .md file for writing.
    mdPath = makeMdPath(id, chap, fname)
    mdFile = io.open(mdPath, "tw", buffering=1, encoding='utf-8', newline='\n')
    
    # Read input file
    if os.access(fullpath, os.F_OK):
        f = open(fullpath, 'r')
        notes = json.load(f)
        f.close()

    for note in notes:
        title = unicode(note['title']).strip()
        body = unicode(note['body']).strip()
        mdFile.write(u'# ' + title + u'\n\n')
        mdFile.write(body + u'\n\n')
    mdFile.close()

# This method is called to convert the text files in the specified chapter folder
# If it is not a chapter folder
def convertChapter(bookId, dir, fullpath):
    for fname in os.listdir(fullpath):
        if isChunk(fname):
            convertFile(bookId, dir, fname, os.path.join(fullpath, fname))

# Determines if the specified path is a book folder, and processes it if so.
def convertBook(path):
    bookfolder = os.path.split(path)[1]
    bookId = getBookId(bookfolder)
    bookTitle = getBookTitle(bookId)
    if bookId and bookTitle:
        sys.stdout.write("\nConverting: " + bookfolder)
        sys.stdout.flush()
        for dir in os.listdir(path):
            if isChapter(dir):
                # sys.stdout.write( " " + dir )
                convertChapter(bookId, dir, os.path.join(path, dir))
        appendToManifest(bookfolder, bookId, bookTitle)
    return bookTitle
 
# Converts the book or books contained in the specified folder
def convert(dir):
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
    if os.path.isfile( makeManifestPath() ):
        os.remove( makeManifestPath() )
    if not convertBook(dir):
        for directory in os.listdir(dir):
            folder = os.path.join(dir, directory)
            convertBook(folder)


# Processes each directory and its files one at a time
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python txt2md <folder>\n  Use . for current folder.\n")
    elif sys.argv[1] == 'hard-coded-path':
        convert(r'C:\Users\Larry\Documents\GitHub\Kannada\BCS.kn_tn')
    else:       # the first command line argument presumed to be a folder
        convert(sys.argv[1])

    print "\nDone."