# AutoCut
Script to analyze quiet parts in Videos and automatically edit them out. Useful for shortening lectures where the professor does a lot of thinking pauses without saying anything :)

## Dependencies: 
  * ffmpeg installed on machine
  * subprocess, wave, numpy, scipy.io wavfile, os, pathlib, shutil

## Guide
  * First time execution to set up required folders (or manually create 'input' folder)
  * Place videofiles in input folder
  * execute the script
  * ???
  * Profit

## Configurable:
  * soundlimit: defines at which threshold someone is speaking, set higher if a lot of background noise (60 default)
  * minduration: minimal duration in seconds of splits
  
  * change render preset from ultrafast to fast or slow for better file compression, but slows down rendering
  
## Known Bugs:
  * Splitting process can take a long time and slows down the further we are in the video, reason is guessed to be ffmpeg related
  * avoid special characters in input, ffmpeg won't recognize them

## TODO:
  * Add optional Speedup of video
  * Add multithreading to analyzing method
  * Add optional limit analyzing with variance of concrete videosplit
