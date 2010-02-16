#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Joshua Ryan Smith (jrsmith@cmu.edu)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2010 Joshua Ryan Smith"
__license__ = "GPL"

"""
Tests the StaibDat class.

These tests test if the StaibDat class can recognize text files that conform 
to the standard winspectro format. They also check that the StaibDat class 
imports the data correctly. Finally, they check to see if the StaibDat class 
can figure out if the imported file is not self-consistent.
"""

__author__ = "Joshua Ryan Smith (jrsmith@cmu.edu)"
__version__ = ""
__date__ = "2010.02.10 18:08"
__copyright__ = "Copyright (c) 2010 Joshua Ryan Smith"
__license__ = "GPL"

from StaibDat import StaibDat
from StaibDat import FormatError
import unittest
import random
import os

class InvalidDataFile(unittest.TestCase):
  """
  Tests instantiation with invalid data files.
  """
  
  def testStaibDatJunkData(self):
    """Data file is total junk."""
    self.assertRaises(FormatError,StaibDat,"testfiles/junkdata.dat")
  
  def testStaibDatMissingMetadata(self):
    """Data file missing metadata section."""
    self.assertRaises(FormatError,StaibDat,"testfiles/missing_metadata.dat")
  
  def testStaibDatMissingReserved(self):
    """Data file missing reserved section."""
    self.assertRaises(FormatError,StaibDat,"testfiles/missing_reserved.dat")
  
  def testStaibDatMissingData(self):
    """Data file missing data section."""
    self.assertRaises(FormatError,StaibDat,"testfiles/missing_data.dat")
  
  def testStaibDatMetadataSpuriousLine(self):
    """Metadata section includes random spurious line."""
    # Pull in the lines from the good data file.
    gd = open("testfiles/good_data.dat","r")
    gdLines = gd.readlines()
    gd.close()
    # Pull in the one spurious line.
    sl = open("testfiles/spurious_line.txt","r")
    slLine = sl.readline()
    sl.close()
    # Create a temporary data file for this test.
    newfile = open("testfiles/metadata_spurious_line.dat","w")
    # Decide where to randomly put the spurious line in the temp data file.
    loc = random.randint(1,19)
    counter = 1
    # Dump the good data and include the spurious line.
    for line in gdLines:
      if counter == loc:
        newfile.write(slLine)
      newfile.write(line)
      counter = counter+1
    newfile.close()
    self.assertRaises(FormatError,StaibDat,"testfiles/metadata_spurious_line.dat")

  def testStaibDatReservedSpuriousLine(self):
    """Reserved section includes random spurious line."""    
    # Pull in the lines from the good data file.
    gd = open("testfiles/good_data.dat","r")
    gdLines = gd.readlines()
    gd.close()
    # Pull in the one spurious line.
    sl = open("testfiles/spurious_line.txt","r")
    slLine = sl.readline()
    sl.close()
    # Create a temporary data file for this test.
    newfile = open("testfiles/reserved_spurious_line.dat","w")
    # Decide where to randomly put the spurious line in the temp data file.
    loc = random.randint(20,23)
    counter = 1
    # Dump the good data and include the spurious line.
    for line in gdLines:
      if counter == loc:
        newfile.write(slLine)
      newfile.write(line)
      counter = counter+1
    newfile.close()
    self.assertRaises(FormatError,StaibDat,"testfiles/reserved_spurious_line.dat")

  def testStaibDatDataSpuriousLine(self):
    """Data section includes random spurious line."""
    # Pull in the lines from the good data file.
    gd = open("testfiles/good_data.dat","r")
    gdLines = gd.readlines()
    gd.close()
    # Pull in the one spurious line.
    sl = open("testfiles/spurious_line.txt","r")
    slLine = sl.readline()
    sl.close()
    # Create a temporary data file for this test.
    newfile = open("testfiles/data_spurious_line.dat","w")
    # Decide where to randomly put the spurious line in the temp data file.
    loc = random.randint(24,831)
    counter = 1
    # Dump the good data and include the spurious line.
    for line in gdLines:
      if counter == loc:
        newfile.write(slLine)
      newfile.write(line)
      counter = counter+1
    newfile.close()
    self.assertRaises(FormatError,StaibDat,"testfiles/data_spurious_line.dat")
  
  def testStaibDatAdditionalStuffAtEnd(self):
    """Otherwise valid file has extra crap at end."""
    self.assertRaises(FormatError,StaibDat,"testfiles/additional_stuff_at_end.dat")
  
  def testStaibDatMissingDataLabels(self):
    """Data section is missing the data labels line."""
    self.assertRaises(FormatError,StaibDat,"testfiles/missing_data_labels.dat")
  
  def testStaibDatSpuriousDataLabesInData(self):
    """Data section has additional spurious data labels line in data lines."""
    pass
  
  def testStaibDatMixedUpSections(self):
    """File has valid sections in the wrong order."""
    self.assertRaises(FormatError,StaibDat,"testfiles/mixed_up_sections.dat")
  
class InconsistantDataFile(unittest.TestCase):
  """
  Tests instantiation with non-self-consistent data files.
  """
  
  def testStaibDatIncorrectDatapoints(self):
    """Data Points line inconsistent with actual number of data points."""
    self.assertRaises(FormatError,StaibDat,"testfiles/incorrect_datapoints.dat")
  
  def testStaibDatIncorrectStartenergy(self):
    """Startenergy line inconsistent with first Basis value."""
    self.assertRaises(FormatError,StaibDat,"testfiles/incorrect_startenergy.dat")
  
  def testStaibDatIncorrectStopenergy(self):
    """Stopenergy line inconsistent with last Basis value."""
    self.assertRaises(FormatError,StaibDat,"testfiles/incorrect_stopenergy.dat")
  
  def testStaibDatInconsistentStepSize(self):
    """Step size between Basis values are not equal."""
    self.assertRaises(FormatError,StaibDat,"testfiles/inconsistent_step_size.dat")
  
  def testStaibDatIncorrectStepwidth(self):
    """Stepwidth line inconsistent with step widths in Basis values."""
    self.assertRaises(FormatError,StaibDat,"testfiles/incorrect_stepwidth.dat")
  
class CorrectlyImportedData(unittest.TestCase):
  """
  Tests to see if the resulting object has the correct data.
  """
  pass

if __name__ == '__main__':
  unittest.main()
