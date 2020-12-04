#Jonas Briguet 26.11.2020
#Script to analyze quiet parts in Videos and automatically edit them out.
#Used dependencies are ffmpeg, wave, numpy, scipy
#input folder is needed with input files, biggest feature of new version is bulk video processing


import subprocess
import wave
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.io import wavfile
import os
import pathlib
import shutil
import time

def PrepareDirectories(workpath, inputpath, outputpath):            #sets up needed directories
    if os.path.exists(workpath):
        shutil.rmtree(workpath)
        os.makedirs(workpath)
        os.makedirs(workpath+r'\\splits')
        os.makedirs(workpath+r'\\ppsplits')
    else:
        os.makedirs(workpath)
        os.makedirs(workpath+r'\\splits')
        os.makedirs(workpath+r'\\ppsplits')

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

def gettime(totalseconds):                          #function to convert seconds into a more readable format
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

def findthreshold(bufferduration, limit, data, threshold, ss, step):            #function to determine the best possible threshold
    start = 0
    end = 0
    cutlist = []
    
    while start < len(data) - bufferduration - 10:
        if np.mean(data[start:start+10]) < limit:
            start = start + 1
            end = start
        else:
            end = start + bufferduration
            while end + threshold < len(data) and np.mean(data[end:end+threshold]) > limit:
                end = end + step
            cutlist.append([start/ss,(end+threshold)/ss])
            end = end + threshold + 1
            start = end

    return cutlist

def Preprocess(vidname, PPthreshold, PPlimit):                                          #function to preprocess input, speeds up later video-editing
    vidpathname = "input/"+vidname
    subprocess.run("ffmpeg -i "+vidpathname+" -crf 30 -preset ultrafast -af afftdn tmp/preprocessed.mp4", capture_output=True)
    subprocess.run("ffmpeg -i tmp/preprocessed.mp4 -vn -ab 1024 -ar 1000 tmp/ppaudio.wav",capture_output=True)
    ss, data = wavfile.read('./tmp/ppaudio.wav')
    data = np.abs(data)
    limit = PPlimit
    duration, totalframes, fps = getVidInfo(str(vidpathname))
    print("--Limit is: "+str(limit))

    print("--Analyzing")
    bufferduration = round(ss)*minduration

    cutlist = findthreshold(bufferduration, limit, data, PPthreshold, ss, 10)

    if(True):
        print("--Skipping preprocessing")
    elif(True or perachieved(cutlist, duration)*100 < 15):
        print("--Skipping preprocessing")
        subprocess.run("ffmpeg -i "+vidpathname+" -crf 30 -preset ultrafast -af afftdn tmp/preprocessed.mp4", capture_output=True)
    else:
        print("--Number of cuts to be made is: "+str(len(cutlist)))
        print("--Video will be "+str(perachieved(cutlist, duration)*100)+" percent shorter.")
        print("--Threshold is: " + str(PPthreshold))
        print("--Cutting")
        x = 0
        while x < len(cutlist):
            split = "ffmpeg -i "+str(vidpathname)
            print("----"+str(round(x/len(cutlist)*100)) + " %")
            while x < len(cutlist) and len(split) < commandlinelength:                                                                          
                split += " -ss "+str(cutlist[x][0])+" -t "+str(cutlist[x][1]-cutlist[x][0])+" -crf 30 -preset ultrafast -af afftdn tmp/ppsplits/"+str(x)+".mp4"
                x = x + 1
            subprocess.run(split,capture_output=True)

        f = os.listdir("tmp/ppsplits")
        with open(str(workpath)+"/ppcliplist.txt", "w") as cliplist:
            for i in range(0, len(f)):
                cliplist.write("file '"+str(pathlib.Path(__file__).parent.absolute())+"\\tmp\\ppsplits\\"+str(i)+".mp4'\n")
            cliplist.close()

        print("--Merging...")
        subprocess.run("ffmpeg -f concat -safe 0 -i "+str(workpath)+"\ppcliplist.txt -c copy tmp/preprocessed.mp4", capture_output=True)

if __name__ == "__main__":
    
    minduration = 1                     #minimal duration of split in seconds
    soundlimit = 80                    #if higher than this value, spoken words are detected
    commandlinelength = 10000            
    speedup = 1.6                       #optional speedup, not yet implemented
    threshold = 50                      #starting threshold, from which it is analyzed upwards
    thresholdlimit = 80                #highest limit
    PPthreshold, PPlimit, PPminduration = 2000, soundlimit/2, 5       #Preprocessing threshold and limit
    Analyzeloud = False                 #determine if manual calibration on spoken segments

    workpath = str(pathlib.Path(__file__).parent.absolute()) + r'\\tmp'
    inputpath = str(pathlib.Path(__file__).parent.absolute()) + r'\\input'
    outputpath = str(pathlib.Path(__file__).parent.absolute()) + r'\\output'

    PrepareDirectories(workpath, inputpath, outputpath)

    vidlist = []
    files = []
    for (dirpath, dirnames, filenames) in os.walk(inputpath):
        files.extend(filenames)

    for vid in files:                                   #added filename conversion: does this work?
        newname = vid
        newname = newname.replace(" ", "-")
        os.rename(inputpath+"/"+vid, inputpath+"/"+newname)
        vidlist.append(newname)

    if(Analyzeloud):                    #automatic calibration on loud videosegments
        print(vidlist[0])
        starttime = input("Start of spoken part(HH:MM:SS.ms): ")
        durationtime = input("Duration of spoken part(in seconds): ")
        subprocess.run('ffmpeg -i input/'+vidlist[0]+' -ss '+starttime+' -t '+durationtime+' -vn -ab 1024 -ar 1000 tmp/quiet.wav',capture_output=True)
        fs, rdata = wavfile.read('./tmp/quiet.wav')
        rdata = np.abs(rdata)
        newsoundlimit = np.mean(rdata)
        soundlimit = min(soundlimit, int(newsoundlimit))

    count = 1
    for vidname in vidlist:
        starttime = time.time()
        print("Processing video "+str(count)+"/"+str(len(vidlist)))
        print("-Preprocessing started")

        pptime = time.time()
        Preprocess(vidname, PPthreshold, PPlimit)
        print("-Preprocessing took "+gettime(time.time()-pptime))
        #print("Speeding up video")
        #subprocess.run('ffmpeg -i input/'+str(vidname)+' -vf "setpts='+str(1.0/speedup)+'*PTS" -filter:a "atempo='+str(speedup)+'" -preset ultrafast tmp/tmp.mp4',capture_output=True)
        #vidpathname = "tmp/tmp.mp4"
        vidpathname = "tmp/preprocessed.mp4"
        duration, totalframes, fps = getVidInfo(str(vidpathname))
        subprocess.run('ffmpeg -i '+str(vidpathname)+' -vn -ab 1024 -ar 1000 -af afftdn tmp/audio.wav',capture_output=True)            #extract audio needed for analysis, normalize, added audio filtering
        ss, data = wavfile.read('./tmp/audio.wav')
        data = np.abs(data)
        limit = int(soundlimit)
        print("--Limit is: "+str(limit))

        print("--Analyzing")                                                                                            #find best fitting threshold
        currentthreshold = threshold
        currentthresholdlimit = thresholdlimit
        bestTH = 0
        bestP = 0.0
        bestCutlist = []
        bufferduration = round(ss)*minduration

        while(currentthreshold <= currentthresholdlimit):
            print("----"+str(round(currentthreshold/currentthresholdlimit*100)) + " %")

            cutlist = findthreshold(bufferduration, limit, data, currentthreshold, ss, 1)
                
            a = perachieved(cutlist, duration)*100
            if a > bestP:
                bestP = a
                bestTH = currentthreshold
                bestCutlist = cutlist
                if currentthreshold >= currentthresholdlimit:
                    currentthresholdlimit += 40
            currentthreshold += 10

        cutlist = bestCutlist
        currentthreshold = bestTH

        print("--Number of cuts to be made is: "+str(len(cutlist)))                                         #create splits using previously computed list of splits
        print("--Video will be "+str(perachieved(cutlist, duration)*100)+"% ("+gettime(perachieved(cutlist, duration)*duration)+") shorter.") #Added time in minutes shorter
        print("--Threshold is: " + str(currentthreshold))
        print("--Cutting")
        x = 0
        splitlist = []
        while x < len(cutlist):
            split = "ffmpeg -i "+str(vidpathname)
            
            while x < len(cutlist) and len(split) < commandlinelength:
                split += " -ss "+str(cutlist[x][0])+" -t "+str(cutlist[x][1]-cutlist[x][0])+" -crf 30 -preset ultrafast tmp/splits/"+str(x)+".mp4"
                x = x + 1
            splitlist.append(split)

        i = 0
        perlimit = 0
        #added predicted ETA
        
        XPhistory = []
        YThistory = []
        for split in splitlist:
            splitstart = time.time()
            subprocess.run(split,capture_output=True)
            i += 1
            percentage = round(i/len(splitlist)*100)
            splitend = time.time()
            XPhistory.append(percentage)
            YThistory.append(splitend-splitstart)
            if(len(XPhistory) > 1 and len(XPhistory) % 4 == 0):
                step = XPhistory[1]-XPhistory[0]
                XP = np.array(XPhistory, 'float')
                YT = np.array(YThistory, 'float')
                XP = np.reshape(XP, (-1, 1))

                poly = PolynomialFeatures(degree=2)
                XP_ = poly.fit_transform(XP)
                model = LinearRegression().fit(XP_, YT)
                
                predictedtime = 0
                per = percentage
                while(per < 101):
                    predict_ = poly.fit_transform([[per]])
                    predictedtime += int(model.predict(predict_))
                    per += step
                print("----ETA: "+gettime(predictedtime))
                print("----"+str(percentage)+"%")

        f = os.listdir("tmp/splits")
        with open(str(workpath)+"/cliplist.txt", "w") as cliplist:
            for i in range(0, len(f)):
                cliplist.write("file '"+str(pathlib.Path(__file__).parent.absolute())+"\\tmp\\splits\\"+str(i)+".mp4'\n")
            cliplist.close()

        print("--Merging...")                                                                                   #merge created splits
        subprocess.run("ffmpeg -f concat -safe 0 -i "+str(workpath)+"\cliplist.txt -c copy output/"+str(vidname), capture_output=True)

        print("--Cleaning up directory...")
        PrepareDirectories(workpath, inputpath, outputpath)
        count += 1
        print("This file took "+gettime(time.time()-starttime)+" to finish.")
    print("Finished processing")
    input("Press key to exit")