import glob
import os

from src.ekn_convert import EknFile

# sample code to convert all ekn files in a directory to csv
os.chdir("D:/mygekko/trend/")
ekn = []

for file in glob.glob("*.ekn"):
    ekn.append(EknFile(file))

for x in ekn:
    x.to_csv()
