from socket import *
from string import *
import sys
import time
import math

# CPSC 4910
# Spring 2014
# Team FitNet
# James Keeler, Daniel Joyner, Noah Falkie

# Description: This program is intended to receive a stream of packets from
# FitSend. This stream should have the following characteristics: every 1081
# packets represent a frame of video, each packet must be 5760 bytes, each
# packet represents a line of pixels of that frame of video, and the video
# must have a resolution of 1920x1080.

# This program is not intended to playback the video. It only reports data loss
# and throughput statistics.

# Once data is received by this program, if the transmission is halted for more
# than 10 seconds the program will exit.


# Writes the contents of a list to a bitmap file.
# Param: myList - a collection of lines of pixels which, together, comprise an image
def writeToFile(myList):
    # Count the number of lines we repair
    counter = 0

    # NULL values in the list mean we dropped packets. We will replace the NULLs 
    # with the list element neighbor.
    # We are done when there are no more NULLs in the list.
    done = False
    while (not done):
        try:
            # Index throws a ValueError exception when the search token isn't found
            i = myList.index('NULL')

            # We "heal" the image by copying the previous element into the current
            # element whenever we find missing data. Missing data results from packet
            # loss. This results in a NULL element. If no NULL elements exist, then
            # there was no packet loss and the previous command would throw an error.
            myList[i] = myList[i-1]

            # We "healed" a line, so bump the counter
            counter += 1

        # There are no NULLs in the list
        except ValueError:
            done = True

    print('Repaired ' + str(counter) + ' lines.')

    # Epoch time will be used so that filenames are always unique
    timestamp = "{0:.4f}".format(time.time())

    # File name will be epoch time .bmp
    filename = timestamp + '.bmp'

    # Open the file. "wb" means write mode, binary file
    file = open(filename,'wb')

    # Write the lines to the image file.
    for line in myList:
        file.write(line)

    # Close the file
    file.close()

host = ''                                           # Defaults to localhost
port = 42524                                        # A random port to be used for communication. MUST MATCH THE PORT OF THE SENDER.
s = socket(AF_INET,SOCK_DGRAM)                      # SOCK_DGRAM denotes the UDP protocol
s.bind((host,port))
addr = (host,port)
buf = 5760                                          # 1920 pixels x 3 color bytes per pixel = 5760 bytes per line
buf += 4                                            # Add 4 bytes for the line number
buf += 4                                            # Add 4 bytes for the frame number

lines = []                                          # This list will hold the lines of image data
for i in range(1082):
    lines.insert(0, 'NULL')                         # Fill the list with NULL values

data,addr = s.recvfrom(buf)                         # Read the first line of the image
header = data[:8]                                   # Get the image header
frameNum = int(header[:4])                          # The first 4 bytes contain the frame number
lineNum = int(header[4:])                           # The next 4 bytes contain the line number

s.settimeout(10)                                    # If data transmission stops for more than 10 seconds, exit

# Counters
count = 0
lossPct = 0.0
throughput = 0.0
timeBegin = time.time()
totalCount = 0
totalLosses = 0
totalThroughput = 0.0
throughputList = []
try:
    while(data):
        count += 1
        
        # Insert the image information into the list at index lineNum
        lines[lineNum] = data[8:]
        prevFrameNum = frameNum

        # If we wait to get the timestamp until the next line of code is 
        # executed, then we will be adding the wait time into the calculation, 
        # making the throughput inaccurate. This will only be used to calculate
        # the time for the last packet sent.
        timeEnd = time.time()

        # Get next line of the image
        data,addr = s.recvfrom(buf)
        header = data[:8]
        # The first 4 bytes contain the frame number
        frameNum = int(header[:4])
        # The next 4 bytes contain the line number
        lineNum = int(header[4:])

        # If the frame number changes 
        # or if we receive line 1081 
        # or if the change in linenum is greater than 700
        # then assume we have started a new image
        #if (prevFrameNum != frameNum or lineNum == 1081 or math.fabs(lineNum - prevLineNum) > 700):
        if (prevFrameNum != frameNum or lineNum == 1081):
            loss = (1081 - float(count)) / 1081
            throughput = count * 5760 * 8 / 1048576     # Megabits per frame
            totalTime = time.time() - timeBegin         # Time to transfer this frame in seconds
            throughput = throughput / totalTime         # Megabits per second
            print('Frame {0:4d}: {1:4d} packets, {2:>6.2%} loss at {3:>5.1f} Mbps'.format(frameNum, count, loss, throughput))
            throughputList.append(throughput)
            totalThroughput += throughput
            totalCount += count
            totalLosses += 1081 - count
            #writeToFile(lines)
            count = 0
            timeBegin = time.time()

except timeout:
    pass

finally:
    loss = (1081 - float(count)) / 1081
    throughput = count * 5760 * 8 / 1048576     # Megabits per frame
    totalTime = timeEnd - timeBegin             # Time to transfer this frame in seconds
    throughput = throughput / totalTime         # Megabits per second
    print('Frame {0:4d}: {1:4d} packets, {2:>6.2%} loss at {3:>5.1f} Mbps'.format(frameNum, count, loss, throughput))
    throughputList.append(throughput)
    totalThroughput += throughput
    totalCount += count
    totalLosses += 1081 - count
    #writeToFile(lines)
    s.close()

    # By sorting the list we can easily get the min and max values
    throughputList.sort()

    print(' ')
    print('Statistics for the receipt of {0} frames of video:'.format(frameNum + 1))
    print('    Packets sent     : {0}'.format((frameNum + 1) * 1081))
    print('    Packets received : {0}'.format(totalCount))
    print('    Packets lost     : {0} ({1:.2%})'.format(totalLosses, float(totalLosses) / float(totalCount)))
    print(' ')
    print('    Max throughput   : {0:>5.1f} Mbps'.format(throughputList[-1]))
    print('    Min throughput   : {0:>5.1f} Mbps'.format(throughputList[0]))
    print('    Avg throughput   : {0:>5.1f} Mbps'.format(totalThroughput / (frameNum + 1)))
