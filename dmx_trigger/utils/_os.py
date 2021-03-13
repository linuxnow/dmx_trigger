# -*- coding: UTF-8 -*-
"""
The DMX Trigger os utility functions
"""

def sibpath(path, sibling):
    """Return the path to a sibling of a file in the filesystem.

    This is useful in conjunction with the special __file__ attribute
    that Python provides for modules, so modules can load associated
    resource files.

    Borrowed from twisted.python.util
    """
    import os.path
    return os.path.join(os.path.dirname(os.path.abspath(path)), sibling)

