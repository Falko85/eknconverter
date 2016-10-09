#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os

from ekn_convert import EknFile

## sample code to convert all ekn files in a directory to csv
os.chdir("D:/mygekko/")
ekn = []

for file in glob.glob("*.ekn"):
    ekn.append(EknFile(file))

for x in ekn:
    x.to_csv()
