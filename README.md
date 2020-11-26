# AutoCut
Script to analyze quiet parts in Videos and automatically edit them out. Useful for shortening lectures where the professor does a lot of thinking pauses without saying anything :)

Dependencies: 
  -ffmpeg installed on machine
  -subprocess, wave, numpy, scipy.io wavfile, os, pathlib, shutil

Guide
  -First time execution to set up required folders
  -After that, drop the videofiles which you want to edit in the input folder and execute the script, easy as that

Configurable:
  -soundlimit: defines at which threshold someone is speaking, set higher if a lot of background noise (60 default)
  -minduration: minimal duration in seconds of splits
  
  -change render preset from ultrafast to fast or slow for better file compression, but slows down rendering
  
Known Bugs:
  -Splitting process can take a long time and slows down the further we are in the video, reason is guessed to be ffmpeg related
