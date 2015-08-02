#!/usr/bin/python3

from containers.songpack import SongPack
import pprint
import json
import os
import sys
import shutil
import time

# MAIN
# C:\dev\cs_site\site_idea\Songs
if __name__ == "__main__":

    # Create prettyprinter object
    pp = pprint.PrettyPrinter(indent=4)

    # Create Batch Object with user specified directory.
    print(">>> parsesongsfolder.py looks through a Songs folder directory containing all "
          "the song packs in a Stepmania directory and creates individual JSONS for "
          "each song pack, containing all chart information for those packs.")

    # Retrieve the directories for all the valid song packs.
    songsDirectory = ""
    songPacks = []
    overallTime = 0.0
    while True:
        try:
            # Retrieve Songs directory from user
            songsDirectory = (input(">>> Input full path to directory of Songs directory: ")).strip()
            jsonsDir = os.path.join(songsDirectory, "jsons")

            # Clean out the 'jsons' directory first. Create it after the song packs are listed.
            if os.path.exists(jsonsDir):
                shutil.rmtree(jsonsDir)
            songPacks = os.listdir(songsDirectory)
            os.makedirs(jsonsDir)
            break
        except:
            print(">>> parsesongsfolder.py: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                         str(sys.exc_info()[1])))

    # Look at listsongpack.py and imitate what it's doing for each song pack.
    # Make a logger for this script.
    jsonsToWrite = []
    totalTime = 0.0
    print(">>> parsesongsfolder.py: MAKE: Making JSONs for the song packs.")
    try:
        for songPack in songPacks:
            songPackDir = os.path.join(songsDirectory,songPack)
            if os.path.isdir(songPackDir):
                try:

                    # Parse the stepfile information for the song pack.
                    print(">>> parsesongsfolder.py: MAKE: Making JSON for Song Pack '" + songPack + "'.")
                    start = time.time()
                    pack = SongPack(songPackDir)
                    pack.retrieveSongFolders() # Initialize search fields and list of folders in batch directory.
                    pack.constructStepfiles(); pack.parseStepfiles() # Make the stepfile objects and parse them.

                    # Get the Song Array (has dictionaries for each chart) from the SongPack object and save it.
                    packName = pack.getPackName()
                    songs = pack.getSongs()
                    jsonsToWrite.append(songs)
                    end = time.time()
                    elapsed = end - start
                    totalTime += elapsed
                    print(">>> parsesongsfolder.py: MAKE: Made JSON. Time Elapsed: " + str(round(elapsed,3)) + " seconds.")
                    
                except:
                    print(">>> parsesongsfolder.py: MAKE: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                 str(sys.exc_info()[1])))
            else:
                continue # This means it wasn't a directory
    except:
        print(">>> parsesongsfolder.py: MAKE: MAKE: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                     str(sys.exc_info()[1])))
    print(">>> parsesongsfolder.py: MAKE: JSONs for Song Packs made in " + str(round(totalTime,3)) + " seconds.")
    overallTime += totalTime

    # Now that we have the list of song pack information, we can dump them out
    # into JSONs in a directory called "jsons".
    print(">>> parsesongsfolder.py: WRITE: Found " + str(len(jsonsToWrite)) + " song packs. Writing out JSONs.")
    totalTime = 0.0
    try:
        jsonsDir = os.path.join(songsDirectory, "jsons")
        if os.path.isdir(jsonsDir):
            counter = len(jsonsToWrite)
            for jsonToWrite in jsonsToWrite:
                # Get the name of the song pack, then write its song charts out to a JSON file.
                start = time.time()
                packName = jsonToWrite[0]['pack']
                print(">>> parsesongsfolder.py: WRITE: Writing JSON file for Song Pack '" + packName + "'. " + str(len(jsonToWrite)) + " songs found.")
                outFilePath = os.path.join(jsonsDir, packName + ".json")
                with open(outFilePath, 'w') as outFile:
                    json.dump(jsonToWrite, outFile, indent=4)
                outFile.close()
                end = time.time()
                elapsed = round(end - start,3)
                totalTime += elapsed
                counter -= 1
                print(">>> parsesongsfolder.py: WRITE: " + str(counter) + " Song Packs left. Successfully wrote JSON. Time Elapsed: " + str(round(elapsed,3)) + " seconds.")
        else:
            print(">>> parsesongsfolder.py: WRITE: jsons directory not successfully created.")
    except:
        print(">>> parsesongsfolder.py: WRITE: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                     str(sys.exc_info()[1])))
    print(">>> parsesongsfolder.py: WRITE: JSONs for Song Packs written in " + str(round(totalTime,3)) + " seconds.")
    overallTime += totalTime
    print(">>> parsesongsfolder.py: Total Time Elapsed: " + str(round(overallTime,3)) + " seconds.")
    print(">>> parsesongsfolder.py: Finished writing JSONs for the song packs. See '" + jsonsDir + "' for these files.")


# NOPE
