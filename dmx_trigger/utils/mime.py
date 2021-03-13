# -*- coding: UTF-8 -*-
"""
The DMX Trigger mime type utility functions
"""

def get_content_type(filename):
    ext = filename.split(".")[-1]
    content_types = {"png": "image/png",
                     "jpg": "image/jpeg",
                     "gif": "image/gif",
                     "ico": "image/x-icon",
                     "css": "text/css",
                     "html": "text/html",
                     "txt": "text/plain",
                     "json": "application/json",
                     "xml": "application/xml"}
    return content_types.get(ext, "text/plain")

