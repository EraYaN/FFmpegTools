#!/usr/bin/env python3
# Concats files that are dropped on this script.

import os
import time
import subprocess as sp
import argparse
from natsort import natsorted

def generateOutputFilePath(files):
    extensions = list(set(map(lambda x: os.path.splitext(x)[1].lower(), files)))
    extension = '.mkv'
    if len(extensions)==1:
        extension=extensions[0]
    return "{}.concat{}".format(os.path.commonprefix(files),extension)

def generateInputFileList(files):
    sortedFiles = natsorted(files, key=lambda i: os.path.splitext(os.path.basename(i))[0])
    for file in sortedFiles:
        yield "file '{0}'".format(file)

def convertChapters(files, outputFile=None):
    if len(files) == 0:
        print("ERROR: No input files given.")
        return False
    for file in files:
        if not os.path.exists(file):
            print("ERROR: {} does not exist.".format(file))
            return False
    print("Concatenating {} files...".format(len(files)))
    
    if outputFile is not None:
        outputFilePath = outputFile
    else:
        outputFilePath = generateOutputFilePath(files)
    print("Outputting to: {}".format(outputFilePath))

    # Build command
    command = [
        "ffmpeg",
        '-hide_banner', # Hide banner
        '-loglevel','warning', # Hide all the stream info
        '-stats', # Do display stats so something moves
        '-y', # Overwrite existsing files   
        '-f', 'concat', # Overwrite existsing files    
        '-i', '-', # Input file         
        '-map', '0', # Take all streams            
        '-c', 'copy', # Do a a stream copy           
        outputFilePath # The output path
    ]
    print("Command: {0}".format(' '.join(command).encode('ascii', 'ignore')))
    try:
        # ffmpeg requires an output file and so it errors
        # when it does not get one
        start = time.time()
        p = sp.Popen(command,stdin=sp.PIPE)
        inputString = '\n'.join(generateInputFileList(files))
        print(inputString.encode('ascii', 'ignore'))
        p.communicate(input=inputString.encode('utf-8'))
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
    parser.add_argument("-o", "--output",dest="outputFile", help="Output File")
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()
    
    files = args.files

    if args.outputFile:
        result = convertChapters(files,args.outputFile)
    else:
        result = convertChapters(files)

    if result:
        print("Succesfully concatenated all input files.")
    else:
        print("Some error occurred")

    
