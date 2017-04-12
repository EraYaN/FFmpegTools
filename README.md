# FFmpegTools
A collection of FFmpeg tools and scripts written in Python.

## FFmpegChapterSplit
Uses ffprobe and ffmpeg to extract a file by chapter

Adapted by Erwin (EraYaN) from Harry's version found [here](http://stackoverflow.com/questions/30305953/is-there-an-elegant-way-to-split-a-file-by-chapter-using-ffmpeg/36735195#36735195).
Example for to mov (Premiere Pro CC likes these), for the chapters 1, 3, 6 and 23 from the source file.

```shell
FFmpegChapterSplit.py -f "\\SERVER\media\source_file.mkv" --force-extension mov -c 1,3,6,23
```
Note: This command WILL overwrite without asking.

Output:
```
\\SERVER\media\source_file\  
   1 - Chapter 1 Title.mov
   3 - Chapter 3 Title.mov
   6 - Chapter 6 Title.mov
   23 - Chapter 23 Title.mov
```  
