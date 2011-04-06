#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Tests the StaibDat class.

These tests test if the StaibDat class can recognize text files that conform 
to the standard winspectro format. They also check that the StaibDat class 
imports the data correctly. Finally, they check to see if the StaibDat class 
can figure out if the imported file is not self-consistent.
"""

from tfan_parsers import StaibDat
from tfan_parsers import FormatError
import unittest
import random
import os
import numpy

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
  
class APITest(unittest.TestCase):
  """
  Tests to see if the API is correct.
  """
  
  filename = "testfiles/good_data.dat"
  
  def testStaibDatfilenameExist(self):
    """filename key should exist."""
    SD = StaibDat(self.filename)
    self.assertTrue("filename" in SD)
    
  def testStaibDatfilenameStr(self):
    """filename data should be a string."""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD["filename"]),type(str()))
    
  def testStaibDatfilenameVal(self):
    """filename data should match instantiating string."""
    SD = StaibDat(self.filename)
    self.assertEqual(SD["filename"],self.filename)
    
  def testStaibDatfileTextExist(self):
    """fileText key should exist."""
    SD = StaibDat(self.filename)
    self.assertTrue("fileText" in SD)
    
  def testStaibDatfileTextStr(self):
    """fileText data should be a string."""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD["fileText"]),type(list()))
    
  def testStaibDatfileTextVal(self):
    """fileText data should match the data in the file."""
    # open the data file and turn it into a list with readlines.
    datFile = open(self.filename,"r")
    fileTextList = datFile.readlines()
    datFile.close()
    SD = StaibDat(self.filename)
    self.assertEqual(fileTextList,SD["fileText"])
    
  def testStaibDatKEExist(self):
    """KE key should exist."""
    SD = StaibDat(self.filename)
    self.assertTrue("KE" in SD)
    
  def testStaibDatKEArray(self):
    """KE data should be a numpy array."""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD["KE"]),numpy.ndarray)
    
  def testStaibDatKESize(self):
    """KE array should be the correct size."""
    SD = StaibDat(self.filename)
    self.assertEqual(SD["KE"].shape[0],SD["DataPoints"])
    
  def testStaibDatKEValues(self):
    """KE array should have the proper values."""
    SD = StaibDat(self.filename)
    KEArray = numpy.array(SD["Basis"]["value"])/1000
    self.assertTrue(all(KEArray == SD["KE"]))

  def testStaibDatBEExist(self):
    """BE key should exist."""
    SD = StaibDat(self.filename)
    self.assertTrue("BE" in SD)
    
  def testStaibDatBEArray(self):
    """BE data should be a numpy array."""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD["BE"]),numpy.ndarray)
    
  def testStaibDatBESize(self):
    """BE array should be the correct size."""
    SD = StaibDat(self.filename)
    self.assertEqual(SD["BE"].shape[0],SD["DataPoints"])
    
  def testStaibDatBEValues(self):
    """BE array should have the proper values."""
    SD = StaibDat(self.filename)
    BEArray = SD["SourceEnergy"] - (numpy.array(SD["Basis"]["value"])/1000)
    self.assertTrue(all(BEArray == SD["BE"]))
  
  def testStaibDatC1Exist(self):
    """C1 key should exist."""
    SD = StaibDat(self.filename)
    self.assertTrue("C1" in SD)
    
  def testStaibDatC1Array(self):
    """C1 data should be a numpy array."""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD["C1"]),numpy.ndarray)
    
  def testStaibDatC1Size(self):
    """C1 array should be the correct size."""
    SD = StaibDat(self.filename)
    self.assertEqual(SD["C1"].shape[0],SD["DataPoints"])
    
  def testStaibDatC1Values(self):
    """C1 array should have the proper values."""
    SD = StaibDat(self.filename)
    C1Array = numpy.array(SD["Channel_1"]["value"])
    self.assertTrue(all(C1Array == SD["C1"]))
    
  def testStaibDatC2Exist(self):
    """C2 key should exist."""
    SD = StaibDat(self.filename)
    self.assertTrue("C2" in SD)
    
  def testStaibDatC2Array(self):
    """C2 data should be a numpy array."""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD["C2"]),numpy.ndarray)
    
  def testStaibDatC2Size(self):
    """C2 array should be the correct size."""
    SD = StaibDat(self.filename)
    self.assertEqual(SD["C2"].shape[0],SD["DataPoints"])
    
  def testStaibDatC2Values(self):
    """C2 array should have the proper values."""
    SD = StaibDat(self.filename)
    C2Array = numpy.array(SD["Channel_2"]["value"])
    self.assertTrue(all(C2Array == SD["C2"]))
  
  def testStaibDatsmoothArray(self):
    """smooth should return a numpy array"""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD.smooth("C1")),numpy.ndarray)
  
  def testStaibDatsmoothSize(self):
    """smooth should return an array of the same size as what it was given"""
    SD = StaibDat(self.filename)
    self.assertEqual(SD.smooth("C1").shape[0],SD["C1"].shape[0])
  
  def testStaibDatsmoothInvalidKey(self):
    """smooth should fail if its given a key that doesn't refer to a numpy array"""
    SD = StaibDat(self.filename)
    self.assertRaises(TypeError,StaibDat.smooth,"fileText")
  
  def testStaibDatdifferentiateArray(self):
    """differentiate should return a numpy array"""
    SD = StaibDat(self.filename)
    self.assertEqual(type(SD.differentiate("C1")),numpy.ndarray)
  
  def testStaibDatdifferentiateSize(self):
    """differentiate should return an array of the same size as what it was given"""
    SD = StaibDat(self.filename)
    self.assertEqual(SD.differentiate("C1").shape[0],SD["C1"].shape[0])
  
  def testStaibDatdifferentiateInvalidKey(self):
    """differentiate should fail if its given a key that doesn't refer to a numpy array"""
    SD = StaibDat(self.filename)
    self.assertRaises(TypeError,StaibDat.differentiate,"fileText")
  
if __name__ == '__main__':
  unittest.main()
