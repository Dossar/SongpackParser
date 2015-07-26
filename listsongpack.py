#!/usr/bin/python3

from containers.songpack import SongPack
import pprint
import json
import os

# MAIN
# C:\dev\cs_site\site_idea\Sexuality Violation
if __name__ == "__main__":

    # Create prettyprinter object
    pp = pprint.PrettyPrinter(indent=4)

    # Create Batch Object with user specified directory.
    print(">>> listsongpack.py looks through a song pack directory and retrieves song "
          "information from it including chart information.")
    songPackPath = (input(">>> Input full path to directory of Song Pack Folder: ")).strip()
    pack = SongPack(songPackPath)

    # Initialize search fields and list of folders in batch directory.
    print(">>> Getting list of folders in song pack directory.")
    pack.retrieveSongFolders()
    print(pack)

    # Make the stepfile objects and parse them.
    print(">>> Constructing Simfile Objects and parsing them.")
    pack.constructStepfiles()
    pack.parseStepfiles()
    print(pack)

    """
    The following would be for checking each Stepfile object.
    """
    # for stepfile in pack.getStepfiles():
    #    pp.pprint(stepfile.getSongDict())

    """
    The following would be for checking the SongPack object.
    """
    # pp.pprint(pack.getSongs())

    """
    Try to get the Song Dictionary from the SongPack object and then write it out
    to a file, similar to JSON stuff.
    """
    print(">>> Writing JSON file for song pack.")
    packName = pack.getPackName()
    songs = pack.getSongs()
    outFilePath = os.path.join(songPackPath, packName + ".json")
    with open(outFilePath, 'w') as outFile:
        json.dump(songs, outFile, indent=4)
    outFile.close()
    print(">>> Successfully wrote JSON file.")
    


# NOPE
