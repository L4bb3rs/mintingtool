#-*- coding: utf-8 -*-

import hashlib
import requests

def sha256Checksum(filePath, fileUrl):
    m = hashlib.sha256()
    if fileUrl==None:
        with open(filePath, 'rb') as fh:
            m = hashlib.sha256()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()
    else:
        r = requests.get(fileUrl)
        for data in r.iter_content(8192):
             m.update(data)
        return m.hexdigest()
