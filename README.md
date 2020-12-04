# AutoCut
Script to analyze quiet parts in Videos and automatically edit them out. Useful for shortening lectures where the professor does a lot of thinking pauses without saying anything :)

## Features
  * Automatic denoising of audio using ffmpeg and FFT
  * Calculates how much time is saved for each video
  * Bulk Video Processing
  * Automatically optimizes for best threshold (lower limit configurable)
  * Little to none Audio Clipping

## Dependencies: 
  * ffmpeg installed on machine
  * libraries: subprocess, wave, numpy, scipy.io wavfile, os, pathlib, shutil, scikit-learn

## Guide
  * First time execution to set up required folders (or manually create 'input' folder)
  * Place videofiles in input folder
  * execute the script
  * ???
  * Profit

## Configurable:
  * soundlimit: defines at which threshold speech is detected (higher = more aggressive cutting)
  * minduration: minimal duration in seconds of splits (higher -> less splits and more performance, but less silent parts cut out, consider reducing if on mobile)
  * change render preset from ultrafast to fast or slow for better file compression, but slows down rendering
  
## Known Bugs:
  * Be careful not to pause ffmpeg by accident while executing

## TODO:
  * Add optional Speedup of video
  * Add multithreading to analyzing method
  * Add optional limit analyzing with variance of concrete videosplit
  * Detect stutters and more, but can probably just be achieved with machine learning and lots of data, which I don't have on my hands right now
