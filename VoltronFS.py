import stat
import errno
import fuse
import numpy as np
import sys

fuse.fuse_python_api = (0, 2)

class VoltronFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.root = '/'

    # Nonimportant but still somehow important bits
  
    def getattr(self, path):
        return os.lstat("." + path)
    
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

    #Important Bits

    def read(self, path, size, offset):
        return 0

    def write(self, path, buf, offset):
        return 0
                         
    def RNG():
        return 0

    def GetStamps():
        return 0

    def DumpStamps():
        return 0

    #Having trouble figuring out how the main should work in these things
def main():
    server = VoltronFS();
    #usage="""
    #    Voltron: A filesystem to create random numbers and write them to
    #    files by our powers combined.
    #    """ + fuse.Fuse.fusage
    #server = VoltronFS(version="%prog " + fuse.__version__,usage=usage,
    #                   dash_s_do='setsingle')
    #server.parser.add_option(mountopt="root", metavar="PATH", default='/',
    #         help="mirror filesystem from under PATH [default: %default]")
    #server.parse(values=server, errex=1)
    #
    #server.main()
    
if __name__ == '__main__':
    main()
