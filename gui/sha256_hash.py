#-*- coding: utf-8 -*-

import hashlib
import requests

def sha256Checksum(filePath, fileUrl):
    m = hashlib.sha256()
    if fileUrl is None:
        with open(filePath, 'rb') as fh:
            m = hashlib.sha256()
            while True:
                if data := fh.read(8192):
                    m.update(data)
                else:
                    break
            return m.hexdigest()
    else:
        r = requests.get(fileUrl)
        for data in r.iter_content(8192):
            m.update(data)
        return m.hexdigest()
