#!/usr/bin/env python3
# Uses ffprobe and ffmpeg to extract a file by chapter
# Adapted by Erwin (EraYaN) from Harry's version found at http://stackoverflow.com/questions/30305953/is-there-an-elegant-way-to-split-a-file-by-chapter-using-ffmpeg/36735195#36735195

# Example for to mov (Premiere Pro CC likes these): 
#   FFmpegChapterSplit.py -f "\\SERVER\media\source_file.mkv" --force-extension mov -c 1,3,6,23 for the chapters 1, 3, 6 and 23 from the source file.
# Note: This command WILL overwrite without asking.
# Output:
#   \\SERVER\media\source_file\
#       1 - Chapter 1 Title.mov
#       3 - Chapter 3 Title.mov
#       6 - Chapter 6 Title.mov
#       23 - Chapter 23 Title.mov

import os
import re
import time
import subprocess as sp
from os.path import basename
import argparse
import json
from math import floor

def CoarseRound(x, base=5):
    return float(base * round(float(x)/base))

def CoarseFloor(x, base=5):
    return float(base * floor(float(x)/base))

def parseChapters(filename):
    chapters = []    
    command = ["ffprobe", '-i', filename, '-v', 'quiet', '-print_format', 'json', '-show_chapters']
    output = ""
    m = None
    title = None
    chapter_match = None
    try:
        # ffmpeg requires an output file and so it errors
        # when it does not get one so we need to capture stderr,
        # not stdout.
        output = sp.check_output(command, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        output = e.output

    chapters = json.loads(output.decode("utf-8"))['chapters']

    print('Loaded {} chapters from media file.'.format(len(chapters)))

    return chapters

def getChapters(inputFile,includedChapters=[], forceExtension=None):
    
    chapters_raw = parseChapters(inputFile)
    fbase, fext = os.path.splitext(inputFile)
    path, file = os.path.split(inputFile)
    newdir, fext = os.path.splitext(basename(inputFile))

    if not os.path.exists(path + "/" + newdir):
        os.mkdir(path + "/" + newdir)

    if forceExtension:
        fext = '.' + forceExtension
    
    filteredChapters = []
    chap_num = 0
    for chap in chapters_raw:
        chap_num += 1
        if len(includedChapters) > 0 and chap_num not in includedChapters:
            print("Skipping chapter {}".format(chap_num))
            continue   
        
        chap['tags']['title'] = chap['tags']['title'].replace('/',':')
        chap['tags']['title'] = chap['tags']['title'].replace("'","\'")
        # Strip out any characters Windows does not like and this should work on all other systems as well, because they should be less restrictive.
        chap['outfile'] = path + "/" + newdir + "/" + str(chap_num) + ' - ' + re.sub("[\"%/<>^|?\\/]", '_', chap['tags']['title']) + fext
        
        print("Added chapter {} for extraction. From {} to {} into {}".format(chap_num,chap['start_time'],chap['end_time'],chap['outfile'].encode('ascii', 'ignore')))
        filteredChapters.append(chap)
        
    return filteredChapters

def convertChapters(chapters, inputFile):
    for chap in chapters:
        # Build command
        command = [
            "ffmpeg",
            '-hide_banner', # Hide banner
            '-loglevel','warning', # Hide all the stream info
            '-stats', # Do display stats so something moves
            '-y', # Overwrite existsing files
            '-ss', str(chap['start_time']), # Do a input keyframe seek (much faster)
            '-i', inputFile, # Input file         
            '-map', 'v:0', # Take all video streams
            '-map', 'a:0', # Take all audio streams
            #'-map', 's:0', # Take all subtitle streams
            '-c', 'copy', # Doa a stream copy
            '-t', str(float(chap['end_time']) - float(chap['start_time'])), # Enter the duration of the clip.
            chap['outfile'] # The output path
        ]
        print("Command: {0}".format(' '.join(command).encode('ascii', 'ignore')))
        try:
            # ffmpeg requires an output file and so it errors
            # when it does not get one
            start = time.time()
            p = sp.Popen(command)
            p.communicate()
            end = time.time()
            print("File conversion completed in {} seconds.".format(end - start))
            #pass
        except sp.CalledProcessError as e:
            output = e.output
            raise RuntimeError("command '{}' returned with error (code {}): {}".format(e.cmd, e.returncode, e.output.encode('ascii', 'ignore')))    
            return False

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='FFMpegChapterSplitter',description='Extract ffmpeg chapters')
    parser.add_argument("-f", "--file",dest="inputFile", help="Input File", metavar="FILE", required=True)
    parser.add_argument("--force-extension",action="store", default=None, dest="forceExtension", help="Force output to specified extension, eg 'mp4', 'mov'")
    parser.add_argument("-c", "--chapters", action='store', dest='includedChapters', type=lambda x: x.split(','), help="The chapters to be converted, default is all. As a comma seperated list of chapter numbers, starting on 1.")
    args = parser.parse_args()

    inputFile = args.inputFile
    forceExtension = args.forceExtension
    if args.includedChapters:
        includedChapters = [int(i) for i in args.includedChapters]
    else:
        includedChapters = []

    chapters = getChapters(inputFile,includedChapters,forceExtension)
    if convertChapters(chapters,inputFile):

        print("Conversion done.")
    else:
        print("Some error occured.")