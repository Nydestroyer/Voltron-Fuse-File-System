#!/usr/bin/env python
import stat
import errno
import fuse
import numpy as np
import sys
import random
import time
import os
import io

fuse.fuse_python_api = (0, 2)

class VoltronFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.root = './'
        self.userfiles = {}
        self.timestampfiles = {"intermediate":
                            os.path.join("../intermediate.txt")
                               ,"timestamps":
                               os.path.join("../ts2.txt")}
        print self.timestampfiles
        print self.userfiles
		
    # Nonimportant but still somehow important bits
  
    def getattr(self, path):
        st = fuse.Stat()
        st.st_mode = stat.S_IFDIR | 0777
        st.st_nlink = 2
        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime

        if path == '/':
            pass
        else:
            return - errno.ENOENT
        return st
        
    def utime(self,path,times):
        print "utime"
        return 0

    def utimens(self, path, times):
        print "utimens"
        return 0

    def link(self, target, name):
        return 0

    def unlink(self, target, name):
        return 0

    def readlink(self, target, name):
        return 0

    def stat(self):
        return 0
    
    def close(self, path):
        name = os.path.basename(path)  #Get the real file name from the path
        if name in self.userfiles:
            self.userfiles[name] = None
        return 0
    
    def open(self, path, flags):
        name = os.path.basename(path)  #Get the real file name from the path
        print "opening"
        if name in self.userfiles:
            return self.userfiles[name]
        else:
            return create(self, path, mode)
        return -errno.EACCES

    def fgetattr(self, path, fh):
        print "blerg"
        return fuse.Stat()

    def fsync(self, path, datasync, fh):
        print "fsync"
        return 1
    
    def flush(self,path,fh):
        print "flushing"
        return 1
    
    def create(self, path, mode, fi=None):
        name = os.path.basename(path)  #Get the real file name from the path
        print "creating"
        self.userfiles[name] = io.StringIO() #Create a fake file stream to store the data
        print self.userfiles
        return self.userfiles[name]

    def readdir(self, path, offset):
        for f in self.userfiles:
            yield fuse.Direntry(f)
        
    # Important Bits

    def read(self, path, size, offset,fh):
        fh.seek(0,os.SEEK_END)
        print "reading"
        for line in RNG(offset):
            fh.write(line)
        return len(size)

    def write(self, path, buf, offset,fh):
        print "writing"
        fh.seek(0,os.SEEK_END)
        for line in GetStamps(offset):
            fh.write(line)
        return 
        
                 
    def RNG(original_numbers):
        reseed = 10

        stamps = GetTimestamps(8 * (original_numbers/reseed))
        numbers = original_numbers
        
        fi = os.open(self.timestampfiles["intermediate"], "w")

        for line in stamps:
            fi.write(line)
            fi.flush()
            fi.close()

        stamps = np.loadtxt(self.timestampfiles["intermediate"])
   	 
        ti = np.diff(stamps)
        til = ti[1:] > ti[:-1]
        til = np.array(til)
        seed = np.packbits(til- 1)
        randnum = []
    
        while(numbers > 0):
            if numbers % reseed == 0:
                random.seed(int(seed[(numbers/reseed)-1]))
            randnum.append(random.getrandbits(8))
            if numbers == 0:
        	return randnum
            numbers -= 1
        return randnum

    def GetStamps(stamps):
        CleanFile()
        fi = os.open(self.timestampfiles["timestamps"], "r")

        lines = fi.readlines()

        fi.close()

        fi = os.open(self.timestampfiles["timestamps"], "w")

        count = stamps

        for line in lines:
            if count == 0:
                fi.write(line)
                fi.flush()
            if count > 0 and count <= starting_count:
                count -= 1
        fi.close()

        return lines[0:stamps]

    # Cleans file for future use. Removes extra spaces and lines with multiple time stamps
    def CleanFile():
        fi = open(self.timestampfiles["timestamps"],"r")
        lines = fi.readlines()
        fi.close()
        fi = open(self.timestampfiles["timestamps"],"w")
        for line in lines:
            try: 
                float(line)
                fi.write(line)
                fi.flush()
            except:
                pass
            
        fi.close()
        

    #Having trouble figuring out how the main should work in these things

    
if __name__ == '__main__':
    server = VoltronFS()
    usage="""
        Voltron: A filesystem to create random numbers and write them to
        files by our powers combined.
        """ + fuse.Fuse.fusage
    server.parse(errex=1)
    
    server.main()
