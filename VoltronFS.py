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
from fuse import Fuse
import tempfile
fuse.fuse_python_api = (0, 2)

def flag2mode(flags):
    md = {os.O_RDONLY: 'r', os.O_WRONLY: 'w', os.O_RDWR: 'w+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m

class VoltronFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.root = '/home/dveling/'
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
        
    def readlink(self, path):
        return 0

    def unlink(self, path):
        return 0
        
    def link(self, path, path1):
        return 0

    def truncate(self, path, len):
        f = open("." + path, "a")
        f.truncate(len)
        f.close()

    def utime(self, path, times):
        return 1
		
    def access(self, path, mode):
        if not os.access("." + path, mode):
            return -EACCES
    
    def close(self, path):
        name = os.path.basename(path)  #Get the real file name from the path
        if name in self.userfiles:
            self.userfiles[name] = None
        return 0

    def open(self, path, flags, mode):
        print "opening"
        return 
    
    def create(self, path, mode, fi=None):
        name = os.path.basename(path)  #Get the real file name from the path
        print "creating"
        self.userfiles[name] = self.VoltronFile(self,path,0,mode) #Create a fake file stream to store the data
        print self.userfiles
        return self.userfiles[name]

    def readdir(self, path, offset):
        for f in self.userfiles:
            yield fuse.Direntry(f)
        
    def statfs(self):
        return os.statvfs(".")
		
    def fsinit(self):
        os.chdir(self.root)

    def read(self, path, size, offset, fh):
        return fh.read(size, offset)

    def write(self, path, buf, offset, fh):
        return fh.write(buf, offset)
    
    # Important Bits
    class VoltronFile(object):

        def __init__(self, path, flags, *mode):
            self.file = tempfile.TemporaryFile('w+b', -1, '','tmp', None)
            self.fd = self.file.fileno()

        def read(self, length, offset):
            print "reading"
            self.file.seek(offset)
            for line in self.RNG(length):
                self.file.write(line)
            return self.file.read(length)

        def write(self, buf, offset):
            print "writing"
            self.file.seek(offset)
            for line in self.GetStamps(buf):
                self.file.write(line)
            return len(buf)

        def release(self, flags):
            self.file.close()

        def fsync(self, isfsyncfile):
            print "fsyncing"
            return 0

        def flush(self):
            print "flushing"
            return 0

        def fgetattr(self):
            print "yep"
            st = fuse.Stat()
            st.st_mode = stat.S_IFDIR | 0777
            st.st_nlink = 1
            st.st_atime = int(time.time())
            st.st_mtime = st.st_atime
            st.st_ctime = st.st_atime
            
            return st

        def ftruncate(self, len):
            print "ftruncating"
            return 0
		
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

    def main(self, *a, **kw):

        self.file_class = self.VoltronFile

        return Fuse.main(self, *a, **kw)
        
    
if __name__ == '__main__':
    server = VoltronFS()
    usage="""
        Voltron: A filesystem to create random numbers and write them to
        files by our powers combined.
        """ + fuse.Fuse.fusage
    server.parse(errex=1)
    
    server.main()
