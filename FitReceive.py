from socket import *
from string import *
import sys
import time

# The server and client MUST use the same port number
host=''
port = 42524
s = socket(AF_INET,SOCK_DGRAM)
s.bind((host,port))

# The server and client MUST use the same buffer size
addr = (host,port)
buf = 8192

data,addr = s.recvfrom(buf)
#print('Received File:',data.strip())
#f = open(data.strip(),'wb')

# Time has a decimal that we need to replace with '_'
t = str(time.time())
#table = str.maketrans('.', '_')

# File name will be epoch time .bmp
filename = t + '.bmp'
f = open(filename,'wb')

data,addr = s.recvfrom(buf)

try:
    while(data):
        f.write(data)
        s.settimeout(2)
        data,addr = s.recvfrom(buf)
except timeout:
    f.close()
    s.close()
    print('Transmission complete.')
