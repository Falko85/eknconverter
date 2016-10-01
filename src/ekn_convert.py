import array
import csv
import os
import re
from datetime import datetime, timedelta


class EknFile():
    """ reads in an ekn file ( My Gekko binary file format to store trend values
    of home automation components ) and provides methods to retrieve this data
    in a human readable way

    Attributes:
        infile (str): filename of the ekn file to be processed.
        room (str, optional): optional room name for the input file.
    """
    frequency = timedelta(minutes=15)
    """15 minutes is the fix timespan between 2 data points"""

    _filetypes = {
        'All.Aussen': ['°C', 'Wetterstation.Außentemperatur'],
        'All.Wind': ['m/s', 'Wetterstation.Wind'],
        'All.Regen': ['l/h', 'Wetterstation.Regen'],
        'All.Lux': ['kLux', 'Wetterstation.Helligkeit'],
        'All.LuxO': ['kLux', 'Wetterstation.Helligkeit OSt'],
        'All.LuxW': ['kLux', 'Wetterstation.Helligkeit West'],
        'Moon.Azimut': ['°', 'Mondstand.Richtung'],
        'Moon.Elevation': ['°', 'Mondstand.Höhhe'],
        'Sun.Azimut': ['°', 'Sonnenstand.Richtung'],
        'Sun.Elevation': ['°', 'Sonnenstand.Höhe'],
        'Energy.': ['Lt.', 'Einstellung Aktuelle Leistung der Energiezähler'],
        'ER': ['°C', 'Einzelraumregelung.Ist-Temperatur'],
        'ER_V': ['°C', 'Einzelraumregelung.Ventilstellung'],
        'ER_S': ['°C', 'Einzelraumregelung.Soll-Temperatur'],
        'MK': ['°C', 'Mischkreis.Ist-Temperatur'],
        'MK_V': ['°C', 'Mischkreis.Ventilstellung'],
        'MK_S': ['°C', 'Mischkreis.Soll-Temperatur'],
        'WW_B': ['°C', 'Puffer&Boiler.'],
        'WW_R': ['°C', 'Puffer&Boiler.'],
        'WW_S': ['°C', 'Puffer&Boiler.']
    }
    """mapping of filenames to metadata, extracted from manual
    first value contains the unit of measurement
    second value contains the description
    """

    def __init__(self, infile, room="not set"):
        """initializing steps:
        extract metadata informations from filename
        read in binary file and convert to list"""

        self.infile = infile
        """input filename"""

        self.infile_name = os.path.basename(infile)
        """filename stripped from path"""

        self.room = room
        """Room the file content is associated to."""

        self.year = int(self.infile_name[0:4])
        """year from filename determines year of the data set"""

        self.name = re.sub("\d+", "", self.infile_name[5:-4])
        """basic name of the input file"""

        try:
            self.position = str(re.search("\d+", self.infile_name[5:-4]).group(0))
            """position number of the file, e.g. ER1 -> 1"""
        except AttributeError:
            self.position = 0

        try:
            self.description = EknFile._filetypes.get(self.name)[1]
            """description of the file according to manual"""

            self.measurement_unit = EknFile._filetypes.get(self.name)[0]
            """measurement unit of the data according to manual"""

        except TypeError:
            self.description = 'Unknown'
            self.measurement_unit = 'Unknown'

        with open(self.infile, "rb") as _in:
            """put infile into an array for further processing"""
            bs = array.array('f', _in.read())

        self._starttime = datetime(self.year, 1, 1, 0, 0)
        self._endtime = datetime(self.year, 12, 31, 23, 45)
        self._currtime = self._starttime
        self.values = []
        __x = 0

        while self._currtime <= self._endtime:
            self.values.append((self._currtime, round(bs[__x], 2)))
            __x += 1
            self._currtime += EknFile.frequency

    def _get_index(self, timestamp):
        """internal function to retrieve index for specific timestamp"""
        self._timestamp = timestamp
        for __x in self.values:
            if __x[0] == self._timestamp:
                return self.values.index(__x)
        return -1

    def get_current(self):
        """return a tuple with the used timestamp (rounded down to last 15 min) and
        the corresponding datapoint, derived from systimestamp"""
        _tm = datetime.now() - EknFile.frequency
        _tm = _tm - timedelta(minutes=_tm.minute % 15,
                              seconds=_tm.second,
                              microseconds=_tm.microsecond)

        return self.values[self._get_index(_tm)]

    def get_all(self):
        """return complete  object containing the completze file"""
        return self.values

    def get(self, fromtime, totime):
        """to do"""
        self._fromtime = fromtime
        self._totime = totime
        return self.values[self._get_index(self._fromtime):self._get_index(self._totime)]

    def to_csv(self, separator=",", header=True, info_text=True, strip_future_values=True):
        """converts the input to a csv file
        Attributes:
            separator: decimal separator, default ","
            header: Column Header (Timestamp and Measurement unit of the file)
            info_text: additional metadata information
            strip_future_values: the file cotnains values for every datapoint in the year, also in the future
            ( with 0 as default value. When set to true, all future values are ignored to reduce file size)
            """

        self._separator = separator
        self.header = header
        self.info_text = info_text
        self.strip_future_values = strip_future_values
        self._tgt_name = self.infile[0:-3] + "csv"
        fieldnames = ['Timestamp', str(self.measurement_unit)]
        print("writing file " + self.infile_name + " at " + datetime.now().strftime(format='%Y-%m-%d %X'))
        _recent_timestamp = self.get_current()[0]

        with open(self._tgt_name, 'w', newline='') as csvfile:
            fw = csv.writer(csvfile, delimiter=';')
            fw.writerow(["# converted with ekn_converter under MIT License"])
            fw.writerow(["# https://github.com/Falko85/ekn_converter"])

            # write metadata
            if self.info_text:
                fw.writerow(["# Original ekn file: " + self.infile_name])
                fw.writerow(["# Year: " + str(self.year)])
                fw.writerow(["# Description: " + self.description])
                fw.writerow(["# Room: " + self.room])
                fw.writerow("")

            # write header
            if self.header:
                fw.writerow(fieldnames)

            # write data
            for x in self.values:
                if self._separator == ",":
                    x = list(x)
                    x[1] = str(x[1]).replace(".", ",")

                if self.strip_future_values == False or _recent_timestamp >= x[0]:
                    fw.writerow([x[0], str(x[1])])
