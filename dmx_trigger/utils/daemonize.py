# -*- coding: UTF-8 -*-
"""
The DMX Trigger daemon utility functions
"""

def forkme(func):
    import os
    import sys

    # default maximum for the number of available file descriptors
    MAXFD = 1024

    # fork a first process
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            os._exit(0)
    except OSError as e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        os._exit(1)
    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)
    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            os._exit(0)
    except OSError as e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        os._exit(1)

    # now I am a daemon! I close all open file descriptors
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError: # ERROR, fd wasn't open to begin with (ignored)
            pass

    # Redirect the standard I/O file descriptors to os.devnull
    # This call to open is guaranteed to return the lowest file descriptor,
    # which will be 0 (stdin), since it was closed above.
    os.open(os.devnull, os.O_RDWR) # standard input (0)

    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1) # standard output (1)
    os.dup2(0, 2) # standard error (2)
    func()

