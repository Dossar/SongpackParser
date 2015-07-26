#!/usr/bin/python3

import os
import re
import sys
import logging

###########
# LOGGERS #
###########

# Date formatting will be the same for all loggers
dateformatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s: %(message)s')

# Make stepfileLogger logger object.
stepfileLogger = logging.getLogger("STEPFILE")
stepfileLogger.setLevel(logging.DEBUG)
stepfileFileH = logging.FileHandler('/tmp/stepfile.log')
stepfileFileH.setLevel(logging.DEBUG)
stepfileConsoleH = logging.StreamHandler()
stepfileConsoleH.setLevel(logging.WARNING)
stepfileFileH.setFormatter(dateformatter)
stepfileConsoleH.setFormatter(dateformatter)
stepfileLogger.addHandler(stepfileFileH)  # File Handler add
stepfileLogger.addHandler(stepfileConsoleH)  # Console Handler add

########################
# FUNCTION DEFINITIONS #
########################

def getSongTitleFromFolder(folder):
    """
    folder is the name of the folder by itself.
    """

    # Placeholder value for title if something goes wrong
    song = "untitled"

    # group(1) here refers to the captured field. Parse stepartist from song folder.
    stepfileLogger.debug("getSongTitleFromFolder: Retrieving song title from folder '%s'", folder)
    try:
        parenthesesArtist = re.search("(.*)\[(.*)\]$", folder)
        bracketArtist = re.search("(.*)\((.*)\)$", folder)
        curlybraceArtist = re.search("(.*)\{(.*)\}$", folder)
        if parenthesesArtist is not None:
            song = parenthesesArtist.group(1).strip()  # Song Title with parentheses stepartist
        if bracketArtist is not None:
            song = bracketArtist.group(1).strip()  # Song Title with brackets stepartist
        if curlybraceArtist is not None:
            song = curlybraceArtist.group(1).strip()  # Song Title with brackets stepartist
    except:
        stepfileLogger.warning("getSongTitleFromFolder: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

    return song

def getStepArtistFromFolder(folder):
    """
    folder is the name of the folder by itself.
    """

    # Placeholder value for title if something goes wrong
    stepArtist = "unspecified"
    
    # group(1) here refers to the captured field. Parse stepartist from song folder.
    stepfileLogger.debug("getStepArtistFromFolder: Retrieving stepartist from folder '%s'", folder)
    try:
        parenthesesArtist = re.search(".*\[(.*)\]$", folder)
        bracketArtist = re.search(".*\((.*)\)$", folder)
        curlybraceArtist = re.search(".*\{(.*)\}$", folder)
        if parenthesesArtist is not None:
            stepArtist = parenthesesArtist.group(1)  # Stepartist with parentheses
        if bracketArtist is not None:
            stepArtist = bracketArtist.group(1)  # Stepartist with brackets
        if curlybraceArtist is not None:
            stepArtist = curlybraceArtist.group(1)  # Stepartist with brackets
    except:
        stepfileLogger.warning("getStepArtistFromFolder: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                          str(sys.exc_info()[1])))

    return stepArtist

def parseBpmString(bpmString):
    """
    This function takes a string representing the comma-separated BPM values
    string from the .sm file and takes the lowest and highest BPM. It returns
    either an array of 1 or 2 in length, where if it's 1 length then it's
    just one BPM (or rounded to one) and 2 in length means there is a clear
    minimum and maximum BPM.
    """
    
    # Get all BPM Change values
    stepfileLogger.debug("parseBpmString: Attempting to find min and max BPM")
    try:
        allBpmChangesList = bpmString.split(',')
        bpmValues = []
        for bpmChange in allBpmChangesList:
            bpm = bpmChange.split('=')[1]
            bpmValues.append(float(bpm))

        # Find the lowest and highest BPM from the list of integers
        lowestBpm = round(min(bpmValues))
        highestBpm = round(max(bpmValues))
        if lowestBpm == highestBpm:
            return [lowestBpm]
        else:
            return [lowestBpm,highestBpm]
    except:
        stepfileLogger.warning("parseBpmString: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                 str(sys.exc_info()[1])))

def getSongInfoFromLines(fileLines):
    """
    This function takes an array of strings (file lines) from an .sm file
    and returns a dictionary representing information about the song not
    related to the step charts.

    The dictionary returned contains the following keys:
    - title
    - subtitle
    - artist
    - bpm
    """
    
    songInfo = {}
    stepfileLogger.debug("getSongInfoFromLines: Attempting to retrieve song information.")
    try:
        for line in fileLines:
            if line.startswith('#'):
                title = re.search("^#TITLE:(.*);$", line)
                subtitle = re.search("^#SUBTITLE:(.*);$", line)
                artist = re.search("^#ARTIST:(.*);$", line)
                bpm = re.search("^#BPMS:(.*);$", line)

                if title is not None:
                    songInfo['title'] = title.group(1)
                if subtitle is not None:
                    songInfo['subtitle'] = subtitle.group(1)
                if artist is not None:
                    songInfo['artist'] = artist.group(1)
                if bpm is not None:
                    songInfo['bpm'] = parseBpmString(bpm.group(1))
    except:
        stepfileLogger.warning("getSongInfoFromLines: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                       str(sys.exc_info()[1])))
        songInfo['title'] = "untitled"
        songInfo['subtitle'] = ""
        songInfo['artist'] = "Unknown Artist"
        songInfo['bpm'] = "0=0"

    # Return the dictionary of song information
    return songInfo

def getChartInfoFromLines(fileLines):
    """
    This function takes an array of strings (file lines) from an .sm file
    and returns an array of dictionaries, where each dictionary represents
    a different charted difficulty for the file.

    The dictionaries contain the following keys:
    - stepper
    - difficulty
    - game
    - rating
    - mine
    - note
    - roll
    - hold
    """

    # Arrays for keeping track of where #NOTES data is.
    linesOfNotes = []
    chartsStartEnd = []

    # Find the #NOTES lines in the .sm file.
    stepfileLogger.debug("getChartInfoFromLines: Finding #NOTES locations in lines of .sm file.")
    try:
        counter = 0
        for line in fileLines:
            counter += 1
            if line.startswith('#'):
                notes = re.search("^(#NOTES:)", line)
                if notes is not None:
                    # print("NOTES: '" + notes.group(1) + "' on line " + str(counter))
                    linesOfNotes.append(counter)
        totalFileLength = counter
    except:
        stepfileLogger.warning("getChartInfoFromLines: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

    # Relate where the #NOTES lines occur so we know where the chart data starts and ends.
    stepfileLogger.debug("getChartInfoFromLines: Relating chart data on which lines it starts and ends.")
    try:
        counter = 0
        for i in range(len(linesOfNotes)):
            if (i+1) == len(linesOfNotes):
                start = linesOfNotes[i] + 5
                end = totalFileLength - 1
                chartsStartEnd.append([start,end])
                break
            else:
                start = linesOfNotes[i] + 5
                end = linesOfNotes[i+1] - 2
                chartsStartEnd.append([start,end])
    except:
        stepfileLogger.warning("getChartInfoFromLines: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

    # Count the step data by making a call to countStepData.
    stepfileLogger.debug("getChartInfoFromLines: Attempting to retrieve stepchart data.")
    try:
        chartArray = countStepData(fileLines, chartsStartEnd)
    except:
        stepfileLogger.warning("getChartInfoFromLines: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))
        chartArray = []
        stepfileLogger.warning("getChartInfoFromLines: Stepchart data is an empty list.")
    return chartArray

def countStepData(fileLines, chartsStartEnd):
    """
    Takes an array of strings (file lines) and an array specifying
    where #NOTES starts and ends. For instance, chartsStartEnd could look like
    [[25,300],[302,500]]

    This function returns an array of dictionaries representing the different
    charted difficulties for the song.
    """

    # Array of dictionaries, each dictionary being a separate charted difficulty.
    stepfileData = []

    # Get the step data for each chart.
    for chart in chartsStartEnd:

        # Initialize dictionary and range of lines for stepchart data
        chartData = {'note':0, 'hold':0, 'roll':0, 'mine':0}
        start = chart[0]
        end = chart[1]

        stepfileLogger.debug("countStepData: Attempting to retrieve non-step data from the chart.")
        try:
            # Get the non-step data for the chart
            gameType = fileLines[start - 5].strip().strip(":")
            stepperCredit = fileLines[start - 4].strip().strip(":")
            difficultyName = fileLines[start - 3].strip().strip(":")
            difficultyRating = fileLines[start - 2].strip().strip(":")

            # Add the above non-step data to the dictionary
            chartData['difficulty'] = difficultyName
            chartData['rating'] = int(difficultyRating)
            chartData['game'] = gameType
            if stepperCredit != "":
                chartData["stepper"] = stepperCredit
            else:
                chartData["stepper"] = "unspecified"
        except:
            stepfileLogger.warning("countStepData: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                    str(sys.exc_info()[1])))
            chartData['difficulty'] = 'Easy'
            chartData['rating'] = 0
            chartData['game'] = 'dance-single'
            chartData['stepper'] = 'unspecified'
            stepfileLogger.warning("countStepData: Something went wrong getting non-step data for the chart.")

        # Go through the range of lines specifying chart notes
        stepfileLogger.debug("countStepData: Counting step data.")
        try:
            for i in range(start,end):
                line = fileLines[i]
                if line.startswith('//'):
                    continue
                elif line.startswith(' '):
                    continue
                elif line.startswith(','):
                    continue
                elif line.startswith(';'):
                    continue
                else:
                    # This means we have a valid line for counting step data
                    notesInLine = line.count('1')
                    holdsInLine = line.count('2')
                    endHoldOrRoll = line.count('3')
                    rollsInLine = line.count('4')
                    minesInLine = line.count('M')

                    # Jumps and hands should only count as single judgments.
                    notes = notesInLine + holdsInLine + rollsInLine
                    if notes > 0:
                        notes = 1
                    
                    chartData['note'] += notes
                    chartData['hold'] += holdsInLine
                    chartData['roll'] += rollsInLine
                    chartData['mine'] += minesInLine
        except:
            stepfileLogger.warning("countStepData: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                    str(sys.exc_info()[1])))
            chartData['note'] = 0
            chartData['hold'] = 0
            chartData['roll'] = 0
            chartData['mine'] = 0
            stepfileLogger.warning("countStepData: Something went wrong counting the step data.")
                
        stepfileData.append(chartData)

    # Return the array of dictionaries representing charts for the song
    return stepfileData

#####################
# CLASS DEFINITIONS #
#####################

class Stepfile():
    """
    This class is a container providing information for a single song.
    Information includes a dictionary and an array of dictionaries.

    songInfo is the dictionary of song information not related to the stepcharts.
    songCharts is the array of dictionaries representing different charts for the song.
    songTitle is here in case something went wrong parsing the sm file.
    stepArtist is here in case something went wrong parsing the sm file.
    """

    def __init__(self, pathToPackFolder, songFolderName, chartFile):
        self.packPath = pathToPackFolder
        self.packName = os.path.basename(os.path.normpath(self.packPath))
        self.songFolder = songFolderName
        self.songFolderPath = os.path.join(self.packPath, self.songFolder)
        self.stepfile = chartFile
        self.stepfilePath = os.path.join(self.songFolderPath, self.stepfile)
        self.stepfileLines = []
        self.songInfo = {}
        self.songCharts = []
        self.songDict = {}

    # String representation to print out for the object
    def __str__(self):
        return """>>> STEPFILE INFORMATION
- packPath: {}
- songFolder: {}
- songFolderPath: {}
- stepfile: {}
- stepfilePath: {}
- songInfo: {}
- songCharts: {}
- songDict: {}""" \
        .format(self.packPath, self.songFolder, self.songFolderPath, self.stepfile, self.stepfilePath,
                self.songInfo, self.songCharts, self.songDict)

    # Getters
    def getSongInfo(self):
        return self.songInfo

    def getSongCharts(self):
        return self.songCharts

    def getSongFolderName(self):
        return self.songFolder

    def getSongTitle(self):
        return self.songInfo['title']

    def getSongDict(self):
        return self.songDict

    def readStepfileLines(self):
        with open(self.stepfilePath) as smFile:
            for line in smFile:
                self.stepfileLines.append(line)
            smFile.close()

    def parseStepfile(self):
        self.readStepfileLines()
        self.songInfo = getSongInfoFromLines(self.stepfileLines)
        self.songCharts = getChartInfoFromLines(self.stepfileLines)

    def createSongDict(self):
        self.songDict['title'] = self.songInfo['title']
        self.songDict['subtitle'] = self.songInfo['subtitle']
        self.songDict['artist'] = self.songInfo['artist']
        self.songDict['bpm'] = self.songInfo['bpm']
        self.songDict['charts'] = self.songCharts
        self.songDict['pack'] = self.packName


