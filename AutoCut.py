import subprocess
import wave
import numpy as np
from scipy.io import wavfile
import os
import pathlib
import shutil
import time
import multiprocessing
from multiprocessing.pool import ThreadPool


def PrepareDirectories(workpath, inputpath, outputpath):
    if os.path.exists(workpath):
        shutil.rmtree(workpath)
        os.makedirs(workpath)
        os.makedirs(workpath+r'\\splits')
    else:
        os.makedirs(workpath)
        os.makedirs(workpath+r'\\splits')

    if not os.path.exists(inputpath):
        os.makedirs(inputpath)
    
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

def cleanInfo(input_str):       #cleans output string of unwanted information
    result = "" 
    for i in range(2, len(input_str)-5): 
        result = result + input_str[i]
    return float(result)

def getVidInfo(vidpathname):        #extract useful information about the file to be cut
    duration = float(cleanInfo(str(subprocess.check_output('ffprobe -i '+vidpathname+' -show_entries format=duration -v quiet -of csv="p=0"'))))
    tframes = float(cleanInfo(str(subprocess.check_output('ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 '+vidpathname,shell=True))))
    fps = tframes/duration
    return duration, tframes, fps

def perachieved(cutlist, originallength):       #function to calculate actual percentage saved
    sum = 0
    for x in cutlist:
        sum += x[1]-x[0]
    difference = originallength-sum

    return difference/originallength

def gettime(totalseconds):
    result = ""
    if totalseconds/3600 >= 1:
        hours = 0
        while(totalseconds/3600 >= 1):
            totalseconds -= 3600
            hours += 1
        result += str(hours)+" hours "
    
    if totalseconds/60 >= 1:
        minutes = 0
        while(totalseconds/60 >= 1):
            totalseconds -= 60
            minutes += 1
        result += str(minutes)+" minutes "
    
    result += str(round(totalseconds))+" seconds"
    return result

def findthreshold(bufferduration, limit, offset, data, threshold, ss):
    start = 0
    end = 0
    cutlist = []
    
    while start < len(data) - bufferduration - 10:
        if np.mean(data[start:start+8]) < limit + offset:
            start = start + 1
            end = start
        else:
            end = start + bufferduration
            while end + threshold < len(data) and np.mean(data[end:end+threshold]) > limit + offset:
                end = end + 1
            cutlist.append([start/ss,(end+threshold)/ss])
            end = end + threshold + 1
            start = end

    return cutlist

if __name__ == "__main__":
    PPthresh, PPlimit = 2, 20       #Preprocessing threshold and limit
    offset = 0 #offset of rms limit
    realthreshold = 0 #lower => more aggressive cutting
    minduration = 2
    soundlimit = 70
    commandlinelength = 5000
    threadcount = multiprocessing.cpu_count()
    speedup = 1.6

    workpath = str(pathlib.Path(__file__).parent.absolute()) + r'\\tmp'
    inputpath = str(pathlib.Path(__file__).parent.absolute()) + r'\\input'
    outputpath = str(pathlib.Path(__file__).parent.absolute()) + r'\\output'

    PrepareDirectories(workpath, inputpath, outputpath)

    vidlist = []
    for (dirpath, dirnames, filenames) in os.walk(inputpath):
        vidlist.extend(filenames)

    count = 1
    for vidname in vidlist:
        starttime = time.time()
        print("Processing video "+str(count)+"/"+str(len(vidlist)))
        #print("Speeding up video")
        #subprocess.run('ffmpeg -i input/'+str(vidname)+' -vf "setpts='+str(1.0/speedup)+'*PTS" -filter:a "atempo='+str(speedup)+'" -preset ultrafast tmp/tmp.mp4',capture_output=True)
        #vidpathname = "tmp/tmp.mp4"
        vidpathname = "input/"+vidname
        duration, totalframes, fps = getVidInfo(str(vidpathname))
        subprocess.run('ffmpeg -i '+str(vidpathname)+' -vn -ab 1024 -ar 1000 tmp/audio.wav',capture_output=True)
        ss, data = wavfile.read('./tmp/audio.wav')
        data = np.abs(data)
        limit = int(soundlimit)
        threshold = int(round(realthreshold*ss))
        print("--Limit is: "+str(limit))

        print("--Analyzing")
        threshold = 50
        thresholdlimit = 150
        bestTH = 0
        bestP = 0.0
        bestCutlist = []
        bufferduration = round(ss)*minduration

        while(threshold <= thresholdlimit):
            print("----"+str(round(threshold/thresholdlimit*100)) + " %")

            cutlist = findthreshold(bufferduration, limit, offset, data, threshold, ss)
                
            a = perachieved(cutlist, duration)*100
            if a > bestP:
                bestP = a
                bestTH = threshold
                bestCutlist = cutlist
                if threshold >= thresholdlimit:
                    thresholdlimit += 40
            threshold += 10

        cutlist = bestCutlist
        threshold = bestTH

        print("--Number of cuts to be made is: "+str(len(cutlist)))
        print("--Video will be "+str(perachieved(cutlist, duration)*100)+" percent shorter.")
        print("--Threshold is: " + str(threshold))
        print("--Cutting")
        x = 0
        while x < len(cutlist):
            split = "ffmpeg -i "+str(vidpathname)
            print("----"+str(round(x/len(cutlist)*100)) + " %")
            while x < len(cutlist) and len(split) < commandlinelength:                                                                          #TODO3: Test if this works
                split += " -ss "+str(cutlist[x][0])+" -t "+str(cutlist[x][1]-cutlist[x][0])+" -crf 30 -preset ultrafast -c:a aac -b:a 48k tmp/splits/"+str(x)+".mp4"
                x = x + 1
            subprocess.run(split,capture_output=True)

        f = os.listdir("tmp/splits")
        with open(str(workpath)+"/cliplist.txt", "w") as cliplist:
            for i in range(0, len(f)):
                cliplist.write("file '"+str(pathlib.Path(__file__).parent.absolute())+"\\tmp\\splits\\"+str(i)+".mp4'\n")
            cliplist.close()

        print("--Merging...")
        subprocess.run("ffmpeg -f concat -safe 0 -i "+str(workpath)+"\cliplist.txt -c copy output/"+str(vidname), capture_output=True)

        print("--Cleaning up directory...")
        PrepareDirectories(workpath, inputpath, outputpath)
        count += 1
        print("This file took "+gettime(time.time()-starttime)+" to finish.")
    print("Finished processing")
    input("Press key to exit")