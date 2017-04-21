import stat
import errno
import fuse
import numpy as np
import sys
import random

fuse.fuse_python_api = (0, 2)

class VoltronFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

    # Nonimportant but still somehow important bits
  
    def getattr(self, path):
        st = fuse.Stat()
        return st
    
    def unlink(self, path):
        return os.unlink("." + path)

    def link(self, path, name):
        return os.link("." + path, "." + name)

    def open(self, path, flags):
        return os.open("." + path, flags)
    
    def close(self, fh):
        return os.close(fh)

    def truncate(self, path, size):
        f = open("." + path, "a")
        f.truncate(len)
        f.close()
    
    def utime(self, path, times):
        os.utime("." + path, times)

    def statfs(self):
        return os.statcfs(".")
    
    def mkdir(self, path, mode):
        os.mkdir("." + path, mode)
    
    def rmdir(self, path):
        os.rmdir("." + path)
    
    def rename(self, pathfrom, pathto):
        os.rename("." + path, "." + path1)
    
    def fsync(self, path, isfsyncfile, fh):
        return self.flush(path, fh)

    def readdir(self, path, offset):
        return os.readdir("." + path, offset)

    # Important Bits

    def read(self, path, size, offset):
        fi = open("." + path, "a")
        for line in RNG(size):
            fi.write(line)

    def write(self, path, buf, offset):
        fi = open("." + path, "a")
        for line in GetStamps(buf):
            fi.write(line)
                         
    def RNG(original_numbers):
        reseed = 10

	stamps = GetTimestamps(8 * (original_numbers/reseed))
	numbers = original_numbers
    
	fi = open("stampintermediate.txt", "w")

	for line in stamps:
            fi.write(line)
            fi.flush()
        fi.close()

	stamps = np.loadtxt("stampintermediate.txt")
   	 
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
        fi = open("ts2.txt", "r")

        lines = fi.readlines()

        fi.close()

        fi = open("ts2.txt", "w")

        count = stamps

        for line in lines:
            if count == 0:
                fi.write(line)
                fi.flush()
            if count > 0 and count <= starting_count:
                count -= 1
        fi.close()

        return lines[0:stamps]

    # Cleans file for future use 
    def CleanFile():
        fi = open("ts2.txt","r")
        lines = fi.readlines()
        fi.close()
        fi = open("ts2.txt","w")
        for line in lines:
            try: 
                float(line)
                fi.write(line)
                fi.flush()
            except:
                pass
            
        fi.close()
        

    #Having trouble figuring out how the main should work in these things
def main():
    server = VoltronFS();
    usage="""
        Voltron: A filesystem to create random numbers and write them to
        files by our powers combined.
        """ + fuse.Fuse.fusage
    server.parse(errex=1)
    
    server.main()
    
if __name__ == '__main__':
    main()
