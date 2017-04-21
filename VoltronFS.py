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
import re
fuse.fuse_python_api = (0, 2)

class VoltronFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.root = '/home/dveling/'
        self.userfiles = {}
        self.timestampfiles = {"intermediate":"/home/dveling/intermediate.txt"
                               ,"timestamps":"/home/dveling/ts2.txt"}
        self.validfilename = re.compile('^[\w,\s-]+\.[A-Za-z]{3}$')
        print self.timestampfiles
        print self.userfiles
        #self.CleanFile()
		
    # Nonimportant but still somehow important bits
  
    def getattr(self, path):
        name = os.path.basename(path)  #Get the real file name from the path
        print "getattr"
        print path
        print self.userfiles
        st = fuse.Stat()
        st.st_mode = stat.S_IFDIR | 0777
        st.st_nlink = 2
        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime
        if self.validfilename.match(name):
            if name in self.userfiles:
                st = self.userfiles[name].fgetattr()
                pass
            else:
                return - errno.ENOENT
        return st
        
    def readlink(self, path):
        print "readlink"
        return 0

    def unlink(self, path):
        print "unlink"
        return 0
        
    def link(self, path, path1):
        print "link"
        return 0

    def truncate(self, path, len):
        print "trunc"
        f = open("." + path, "a")
        f.truncate(len)
        f.close()

    def utime(self, path, times):
        print "utime"
		
    def access(self, path, mode):
        print "access"
        return 
    
    def close(self, path):
        print "close"

    def open(self, path, flags):
        print "opening"
        name = os.path.basename(path)  #Get the real file name from the path
        if name in self.userfiles:
            return self.userfiles[name]
        else:
            return -errno.ENOENT
    
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
        print "reading"
        return fh.read(size, offset)
        #name = os.path.basename(path)  #Get the real file name from the path
        #fh = self.userfiles[name]
        #for line in self.RNG(size):
        #    fh.write(line,offset)

    def write(self, path, buf, offset, fh=None):
        print "writing"
        name = os.path.basename(path)  #Get the real file name from the path 
        fh = self.userfiles[name]
        print path
        for line in self.GetStamps(buf):
            fh.write(line,offset)
        return len(buf)

    def RNG(self,original_numbers):
        reseed = 10
        
        stamps = self.GetStamps(8 * (original_numbers/reseed))
        numbers = original_numbers
        
        fi = io.open(self.timestampfiles["intermediate"],'w+b')
        
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

    def GetStamps(self,stamps):
        print "getting stamps"
        fi = io.open(self.timestampfiles["timestamps"],'r')
        print "got stamps"
        lines = fi.readlines()
        print lines[1:20]
        fi.close()
        print "saving stamps"
        fi = io.open(self.timestampfiles["timestamps"],'w')
        print "saved stamps"
        count = int(stamps)
        print stamps
        print count
        print lines[1:20]
        for line in lines:
            if count == 0:
                fi.write(line)
                fi.flush()
            if count > 0 and count <= stamps:
                count -= 1
        fi.close()

        return lines[0:int(stamps)]

    # Cleans file for future use. Removes extra spaces and lines with multiple time stamps
    def CleanFile(self):
        print "cleaning time stamps file"
        fi = io.open(self.timestampfiles["timestamps"],'r')
        lines = fi.readlines()
        fi.close()
        fi = io.open(self.timestampfiles["timestamps"],'w')
        for line in lines:
            try:
                float(line)
                fi.write(line)
                fi.flush()
            except:
                pass
        fi.close()
        print "clean"

    # Important Bits
    class VoltronFile(object):

        def __init__(self, path, flags, *mode):
            self.file = tempfile.NamedTemporaryFile('w+b', 0, '','tmp', None, False)
            self.fd = self.file.fileno()
            self.data = io.StringIO(u'',u'\n')

        def release(self, flags):
            print "releasing"

        def fsync(self, isfsyncfile):
            print "fsyncing"
            return 0

        def fgetattr(self):
            print "fgetattribute"
            return os.fstat(self.fd)

        def write(self, buf, offset):
            print "writeinfile"
            self.data.seek(0,2)
            self.data.write(buf)
            return len(buf)
        
        def read(self, size, offset):
            print "reading from file"
            self.data.seek(0)
            self.data.seek(offset)
            return self.data.read(offset+size)

        def ftruncate(self, len):
            print "ftruncating"
            return 0
		
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
