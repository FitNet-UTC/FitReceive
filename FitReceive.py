from socket import *
from string import *
import sys
import time

host=''
port = 42524
s = socket(AF_INET,SOCK_DGRAM)
s.bind((host,port))

addr = (host,port)
buf = 5760

# Add 4 bytes for the line number
buf += 4

# This list will hold the lines of image data
lines = []
for i in range(1082):
    lines.insert(0, 'NULL')

# Get header
data,addr = s.recvfrom(buf)

s.settimeout(2)
count = 0
try:
    while(data):
        count += 1
        # The first 4 bytes contain the line number
        lineNum = int(data[:4])
        # Insert the image information into the list at index lineNum
        lines[lineNum] = data[4:]        

        # Get next line of the image
        data,addr = s.recvfrom(buf)

except timeout:
    s.close()    
    print('Transmission complete. Received '+ str(count) + ' packets.')

count = 0
# NULL values in the list mean we dropped packets. We will replace the NULLs 
# with the list element neighbor.
# We are done when there are no more NULLs in the list.
done = False
while (not done):
    try:
        # Index throws a ValueError exception when the search token isn't found
        i = lines.index('NULL')
        lines[i] = lines[i-1]
        count += 1
    except ValueError:
        done = True

print('Repaired ' + str(count) + ' lines.')

# Epoch time will be used to create file name
t = str(time.time())

# File name will be epoch time .bmp
filename = t + '.bmp'
f = open(filename,'wb')
for line in lines:
    f.write(line)
f.close()
