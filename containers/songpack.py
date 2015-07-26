#!/usr/bin/python3

from containers.stepfile import *

###########
# LOGGERS #
###########

# Date formatting will be the same for all loggers
import logging
dateformatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s: %(message)s')

# Make songpackLogger logger object.
songpackLogger = logging.getLogger("SONGPACK")
songpackLogger.setLevel(logging.DEBUG)
songpackFileH = logging.FileHandler('/tmp/songpackContainer.log')
songpackFileH.setLevel(logging.DEBUG)
songpackConsoleH = logging.StreamHandler()
songpackConsoleH.setLevel(logging.WARNING)
songpackFileH.setFormatter(dateformatter)
songpackConsoleH.setFormatter(dateformatter)
songpackLogger.addHandler(songpackFileH)  # File Handler add
songpackLogger.addHandler(songpackConsoleH)  # Console Handler add

#####################
# CLASS DEFINITIONS #
#####################

class SongPack():
    """
    This class is a container that holds Stepfile Objects and
    stores an array of these objects.

    The constructor only requires the user to pass the full
    path to the song pack.

    - packPath: Full path to the song pack folder.
    - packName: Name of the song pack, extracted from the full path.
    - packSongFolders: List of files/folders in the batch folder directory.
    - packSongTitles: List of the song titles for this pack.
    - stepfileList: List of Stepfile objects for each song folder in the pack.
    - songs: List of dictionaries with information for all songs in the pack.
    """

    def __init__(self, fullPackPath):
        self.packPath = fullPackPath
        self.packName = os.path.basename(os.path.normpath(self.packPath))
        self.packSongFolders = []
        self.packSongTitles = []
        self.stepfileList = []
        self.songs = []

    def __str__(self):
        return """>>> SONGPACK INFORMATION
- packPath: {}
- packName: {}
- packSongFolders: {}
- packSongTitles: {}""" \
        .format(self.packPath, self.packName, self.packSongFolders,
                self.packSongTitles)

    # Getters
    def getStepfiles(self):
        return self.stepfileList

    def getSongTitles(self):
        return self.packSongTitles

    def getPackName(self):
        return self.packName

    def getSongs(self):
        return self.songs

    # Setters
    def retrieveSongFolders(self):
        songpackLogger.info("retrieveSongFolders: Retrieving song folder listing in '%s'", self.packPath)
        try:
            self.packSongFolders = os.listdir(self.packPath)
            songpackLogger.info("retrieveSongFolders: Pack Folders are '%s'", self.packSongFolders)
        except:
            songpackLogger.warning("retrieveSongFolders: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                          str(sys.exc_info()[1])))

    def constructStepfiles(self):
        """
        For every song folder in the pack directory, instantiate Stepfile Objects.
        """

        songpackLogger.info("constructStepfiles: Attempting to construct simfile objects in '%s'", self.packPath)

        try:
            for songFolder in self.packSongFolders:
                os.chdir(self.packPath)
                if os.path.isdir(songFolder):
                    try:

                        # Get a listing of the folders
                        folderFiles = os.listdir(songFolder)
                        songpackLogger.debug("constructStepfiles: Folder Files are '%s'", str(folderFiles))

                        # Search for the SM files in the folder
                        for file in folderFiles:
                            smSearch = re.search("(.*\.[sS][mM])$", file)
                            if smSearch is not None:
                                songpackLogger.debug("constructStepfiles: Found SM file in '%s'", songFolder)
                                stepfileToAdd = Stepfile(self.packPath, songFolder, file)
                                songpackLogger.debug("constructStepfiles: Created Stepfile Object for '%s'", songFolder)
                                songpackLogger.debug(stepfileToAdd)
                                self.stepfileList.append(stepfileToAdd) # Add .sm file
                                break
                    except:
                        songpackLogger.warning("constructStepfiles: During Stepfile Creation, {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                                                               str(sys.exc_info()[1])))
                else:
                    continue # This means we didn't have a directory
            songpackLogger.info("constructStepfiles: Created %s simfile objects", str(len(self.stepfileList)))
        except:
            songpackLogger.warning("constructStepfiles: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

    def parseStepfiles(self):
        """
        For every Stepfile Object, parse its SM file for song and chart information. This is
        also where all the song titles are retrieved.

        folder is the name of the folder by itself. It will be turned into the full file path
        However since not every file in the batch could be a folder, keep file cases in mind
        """
        if self.stepfileList is not []:
            songpackLogger.info("parseStepfiles: Parsing batch simfiles")
            for stepfile in self.stepfileList:
                try:
                    songFolder = stepfile.getSongFolderName()
                    songpackLogger.debug("parseStepfiles: Song Folder is '%s'", songFolder)
                    stepfile.parseStepfile()
                    stepfile.createSongDict()
                    songTitle = stepfile.getSongTitle()
                    self.packSongTitles.append(songTitle)
                    self.songs.append(stepfile.getSongDict())
                except:
                    songpackLogger.warning("parseStepfiles: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))

















# NOPE
