# -*- coding: utf-8 -*-

from Errors import FormatError
import re
import numpy
import pyparsing
import pdb

class StaibDat(dict):
  """
  Imports XPS and AES data from Staib .dat file and provides useful features.

  The StaibDat class imports data from a Staib AES or XPS .dat file created by the winspectro software, and makes this data available like a python dictionary. The class tests the data file and the data itself before it returns an object. There is no published standard for the data files generated from the winspectro software; the best guess of the structure of these files is documented in WINSPECTRO_DATA_FILE_STRUCTURE.TXT. This importer is written against the description in that file.
  
  There are several ways to access data in a StaibDat object. Since the winspectro .dat files resemble the key value pairs of a dictionary, the user can directly access the data pulled in from the file simply via the key in the data file. The StaibDat class fixes any keys in the .dat file so that there are no spaces or characters that aren't text, numbers or dashes.
  
  Some of the data in a winspectro .dat file come with explicit units, while some of the data has implicit units. This class will only include the explicit units in the returned StaibDat object. See the WINSPECTRO_DATA_FILE_STRUCTURE.TXT for my best guess about the implicit units of some of the data.
  
  In the winspectro .dat file, there appear to be two main sections: the metadata section at the top, and the data section below. For metadata with units, the StaibDat object returns a dictionary containing the value and unit. Otherwise, accessing the metadata will return only a value. For data, each key returns a dictionary containing a unit (possibly empty) and a list of values.
  
  In addition to keys explicit in the .dat file, the StaibDat class provides the following data and methods for the convenience of the user (units in brackets):
    filename: The name of the file from which the data in the object came.
    fileText: A list with the full text of the data file. Each list item 
      contains a single line of the file.
    KE [eV]: A numpy array containing the kinetic energy value of the electrons.
    BE [eV]: A numpy array containing the binding energy of the electrons 
      calculated using the value of the source energy. Note that this array will
      still be calculated for AES data, but will equal KE since the source 
      energy is zero.
    Cn [count]: A numpy array containing the number of counts for a particular
      energy for channel n. Note that n is an index which can equal any integer.
      When accessing this data, the user will have to specify the index. 
      Attempting to access the literal Cn data will fail.
    smooth: Method that returns a numpy array of smoothed data.
    differentiate: Method that returns numpy array of first derivative of data.
      
  Generally, the user will find it easiest to work with the KE, BE, etc. data as opposed to the dictionary data pulled from the file itself.
  """
  
  #== How the StaibDat class works ==
  #Before any parsing is done, the StaibDat class will verify that the overall structure of the data file is legitimate or otherwise raise an exception. The winspectro data files will be parsed line-by-line. The keys of the StaibDat object will be taken from the appropriate part of the .dat file, explained below. The value of the keys will also be taken from the appropriate part of the .dat file. Once the data has been imported, the StaibDat object will check to see if the data is internally consistant according to the tests listed above.

  #Here's how the various parts of the file will be handled.

  #metadata:
  #The StaibDat object will split the lines on the colon and whitespace, where the string on the left is the dictionary key, and the string on the right is the dictionary value. The StaibDat object will strip any extra whitespace before or after of the key string. Also, the StaibDat object will remove any whitespace in the middle of the key string and compress the remaining text together. The StaibDat object will strip any whitespace before or after the value string also. Some of the metadata lines have either implicit or explicit units. For those lines that don't have units, the StaibDat object will add the key string as the dictionary key and the value string as the dictionary value.

  #Metadata keys have explicit units if the last characters contain brackets enclosing a string, e.g. [V]. The StaibDat object will break off this unit from the key string leaving only a string that can be legitimately used as a dictionary key. Some metadata keys have implicit units defined by me. The StaibDat object will include these units. See the source for more details.

  #For the metadata lines with units, the StaibDat object will use the key string as the dictionary key, but for the the dictionary value, the StaibDat object will use a dictionary with two elements: "value" and "unit". The metadata value and unit will be placed in this dictionary.

  #reserved:
  #Any lines in the reserved section of the data file will be skipped.

  #data:
  #The data block of the file appears to have three columns with some preceding whitespace. The columns are separated by additional whitespace. The first line of the data has a set of labels, where the first label has an explicit unit [mV]. The StaibDat object will make three key-value pairs in the dictionary for the data, one for each column. The dictionary key will be one of the data labels, sans unit. The value for each key will also be a two-element dictionary: value and unit. The unit for the "Basis" column will be [mV], and the unit for the other columns are [counts]. The data will be stored as an array with the value key.

  #== Tests to verify winspectro files. ==
  #* The metadata section should come first, followed by the reserved section, followed by the data section.
  #* There should not be any lines that don't conform to the known three sections.
  #* There should be one and only one line with labels for the data. That line should appear first in the data section.
  #* The number of data lines in the data section should equal the value of the "Data Points" line in the metadata section.
  #* The first Basis value in the data section should almost precisely agree with the "Startenergy[V]" value in the metadata section.
  #* The final Basis value in the data section should almost precisely agree with the "Stop energy[V]" value in the metadata section.
  #* The step size between all the Basis values in the data section should be equal.
  #* The step size between all the Basis values in the data section should almost precisely agree with the "Stepwidth" value in the metadata section.

  
  def __init__(self,filename):
    """
    Instantiation of StaibDat object.

    A StaibDat object is instantiated with a string referring to a .dat file 
    containing AES or XPS data generated by winspectro.
    """
    
    # First, I need to initialize all of the parsing. The following parsers may seem complicated, but I want them to do all of the heavy lifting.
    # Define pyparsing forms for each type of data found in lines of the file.
    unitword = pyparsing.Word(pyparsing.alphas + "%")
    valueword = pyparsing.Word(pyparsing.alphanums + "./=:")
    keyword = pyparsing.Word(pyparsing.alphanums + "-_")
    numvalue = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums))
    
    # In the following I'm using setParseAction because some of the keys and values in the metadata are made up of multiple words. A priori I don't know which ones are, and I don't want to guess and write a bunch of fragile lookup lists and tests that I'll ultimately have to change later. The setParseAction method allows me to combine the multiple words into a single entry in the returned list. See p.19 of McGuire's "Getting Started with Pyparsing" for more details.
    key = pyparsing.OneOrMore(keyword)
    key.setParseAction(lambda tokens: " ".join(tokens))
    unit = pyparsing.Suppress("[") + unitword + pyparsing.Suppress("]") 
    equalsdelimiter = pyparsing.Suppress(":    ")
    value = pyparsing.OneOrMore(valueword)
    value.setParseAction(lambda tokens: " ".join(tokens))
    
    # Again, I'm using setParseAction in this section. For the datavalues section, I'm using setParseAction to coerce the values directly to integers since I know they are supposed to be anyway. I will also need to use Results Names in order to make the extraction of the data from the parsed results doable.
    self.__metadata = key.setResultsName("key") + \
      pyparsing.Optional(unit.setResultsName("unit")) + equalsdelimiter + \
      value.setResultsName("value")
    self.__reserved = pyparsing.Literal("reserved")
    self.__datakeys = pyparsing.Group(keyword.setResultsName("key") + \
      pyparsing.Optional(unit.setResultsName("unit"))) + \
      pyparsing.OneOrMore(pyparsing.Group(keyword.setResultsName("key") + \
      pyparsing.Optional(unit.setResultsName("unit"))))
    self.__datavalues = numvalue.setParseAction(lambda tokens : float(tokens[0])) + \
      pyparsing.OneOrMore(numvalue.setParseAction(lambda tokens : float(tokens[0])))

    #self.__datavalues = pyparsing.Word(pyparsing.nums).setParseAction(lambda tokens : float(tokens[0])) + \
      #pyparsing.OneOrMore(pyparsing.Word(pyparsing.nums).setParseAction(lambda tokens : float(tokens[0])))
      
    # The StaibDat object should know where its data came from.
    self["filename"] = filename
    
    # Pull in the data from the file and close the file.
    datFile = open(filename,"r")
    self["fileText"] = datFile.readlines()
    datFile.close()
    
    # Create a list which labels each line of the file's structure.
    self.__lineTypeList = self.__labelstructure()
    
    # Find the line index of the datakeys in the file. If there isn't one, don't worry because __verifystructure will figure it out.
    if self.__lineTypeList.count("datakeys") != 0:
      self.__datakeysLineIndx = self.__lineTypeList.index("datakeys")
      # Parse the datakeys line and keep the list.
      self.__datakeysList = self.__datakeys.parseString(self["fileText"][self.__datakeysLineIndx])
    
    # Verify the data file has the correct structure.
    self.__verifystructure()
    
    # Parse the text and populate the StaibDat object's data.
    self.__parsetext()
      
    # Verify that the metadata and data in the file agree.
    self.__verifydata()
      
    # Generate the user-friendly KE, C1, etc. numpy arrays.
    self.__userfriendify()
    
  def __labelstructure(self):
    """
    Generate list of line types.
    """
    
    # First, make a line-by-line list of the kind of data contained in each
    # line: either metadata, reserved, datakeys, datavalues, or other.
    lineTypeList = []
    
    for line in self["fileText"]:
      lineTypeList.append(self.__labelline(line))
      
    return lineTypeList
    
    
  def __verifystructure(self):
    """
    Verify structure of imported text.
    
    The data file should only contain lines of type metadata, reserved, datakeys, and datavalues, in that order. Any other type of data indicates an incorrectly formatted .dat file. There should be only one line of datakeys in the .dat file as well. Finally, all lines of datavalues should have the same number of columns, and that number of columns should match the number of datalabels.
    """
    
    # If there is any data in the list of type "other," we know we are dealing with a file containing bad data.
    if "other" in self.__lineTypeList:
      raise FormatError

    # Additionally, there should be a single line of "datakeys" type data in the file.    
    if self.__lineTypeList.count("datakeys") != 1:
      raise FormatError
    
    # In a properly formatted file, the types of lines should come in the following order: metadata, reserved, datakeys, datavalues. If not, the file isn't properly formatted and the import should fail.
    compressedList = []
    
    for lineType in self.__lineTypeList:
      if len(compressedList) == 0:
        compressedList.append(lineType)
      elif lineType != compressedList[-1]:
        compressedList.append(lineType)
        
    if compressedList != ["metadata","reserved","datakeys","datavalues"]:
      raise FormatError
    
    # All of the lines in the data section of the file should have the same number of columns. Furthermore, the number of datakeys should equal the number of columns in the data section of the file.
    for datavaluesLine in self["fileText"][self.__datakeysLineIndx + 1:]:
      # Parse the line
      datavaluesList = self.__datavalues.parseString(datavaluesLine)
      if len(self.__datakeysList) != len(datavaluesList):
        raise FormatError
    

  def __labelline(self,line):
    """
    Returns a string indicating what section of the file the line comes from.
    """
    
    if len(self.__metadata.searchString(line)) != 0:
      return "metadata"
    elif len(self.__reserved.searchString(line)) != 0:
      return "reserved"
    elif len(self.__datavalues.searchString(line)) != 0:
      return "datavalues"
    elif len(self.__datakeys.searchString(line)) != 0:
      return "datakeys"
    else:
      return "other"
      
  def __verifydata(self):
    """
    Compares the values in the metadata section to those in the data section.
    """
    
    # Data Points should equal the number of data points.
    if self["DataPoints"] != len(self["Basis"]["value"]):
      raise FormatError
    
    # The last value of energy should equal Stopenergy.
    if round(self["Stopenergy"]["value"],2) != round(self["Basis"]["value"][-1]/1000,2):
      raise FormatError
       
    # The first value of energy should equal Startenergy.
    if round(self["Startenergy"]["value"],2) != round(self["Basis"]["value"][0]/1000,2):
      raise FormatError
    
    # The difference between each Basis value should be consistent.
    basisList = self["Basis"]["value"][:]
    
    diffList = []
    val = basisList.pop()
    while len(basisList):
      bottomVal = basisList.pop()
      diffList.append(round((val-bottomVal)/1000,2))
      val = bottomVal
      
    if diffList.count(diffList[0]) != len(diffList):
      raise FormatError
    
    # The difference between each Basis value should equal Stepwidth.
    if diffList[0] != round(self["Stepwidth"],2):
      raise FormatError

      
  def __parsetext(self):
    """
    Steps through file text and populates the StaibDat object's data.
    """
    
    # Handle all of the metadata lines.
    for indx, line in enumerate(self.__lineTypeList):
      if line == "metadata":
        # Parse the metadata line.
        metadataLine = self.__metadata.parseString(self["fileText"][indx])
        
        # Try to coerce the value into a number if possible. int first, then float.
        try:
          value = int(metadataLine.value)
        except:
          try:
            value = float(metadataLine.value)
          except:
            value = metadataLine.value
        
        # Compress out any whitespace in the metadata key.
        key = re.sub("\s+","",metadataLine.key)
        
        # Some of the metadata doesn't have units. Try to make an entry with units, but don't fail if there isn't a unit.
        if len(metadataLine.unit) != 0:
          self[key] = {"value":value,
                       "unit":metadataLine.unit}
        else:
          self[key] = value
      else:
        pass
      
    # Handle the data lines, including the datakeys.
    
    # Create dict accessable data in the StaibDat object out of the datakeys.
    for datakey in self.__datakeysList:
      self[datakey.key] = {"value":[]}
      # The unit might not exist. If not, just continue on.
      try:
        self[datakey.key]["unit"] = datakey.unit
      except:
        pass
        
    # Next step through the remaining lines of the file and put each data value in its proper location.
    for datavaluesLine in self["fileText"][self.__datakeysLineIndx + 1:]:
      # Parse the line
      datavaluesList = self.__datavalues.parseString(datavaluesLine)
      # Match each data value to its proper place in the StaibDat object.
      for indx, datavalue in enumerate(datavaluesList):
        self[self.__datakeysList[indx].key]["value"].append(datavalue)
           

  def __userfriendify(self):
    """
    Generate the numpy arrays for KE, BE, and Cn.
    
    According to conversations with Staib, the analyzer has an internal bias
    and therefore we don't have to compensate for the analyzer work function.
    """
    
    self["KE"] = numpy.array(self["Basis"]["value"])/1000
    self["BE"] = self["SourceEnergy"] - self["KE"]
    
    # First, find the line where the datakeys are.
    datakeysLine = self.__lineTypeList.index("datakeys")
    
    # Parse the datakeys and make a list of each one, possibly with units.
    datakeysList = self.__datakeys.parseString(self["fileText"][datakeysLine])
    
    # Assign each additional channel a convenience array.
    for indx,datakey in enumerate(self.__datakeysList[1:]):
      key = "C" + str(indx+1)
      self[key] = numpy.array(self[datakey.key]["value"])
  
  def smooth(self, key, kernel = 13, order = 3):
    """
    Returns numpy array of smoothed data.
    
    This method uses Savitzky-Golay to smooth the data given in one of the 
    StaibDat class's default data arrays. Input arguments as well as their 
    default values are given as follows:
      key: A string indicating which of the object's data should be smoothed 
        (e.g. C1, C2).
      kernel: A positive integer giving the number of points the smoothing 
        algorithm should consider. Default = 13.
      order: A positive integer giving the order of the polynomial used in the 
        smoothing algorithm. Default = 3.
        
    The implementation of Savitzky-Golay was wholesale copied and slightly 
    modified from the SciPy cookbook: 
      http://www.scipy.org/Cookbook/SavitzkyGolay

    See the original Savitzky-Golay paper at DOI: 10.1021/ac60214a047
    """

    return self.__savitzky_golay(self[key],kernel,order,deriv = 0)
  
  def differentiate(self, key, kernel = 13, order= 3):
    """
    Returns numpy array of approximation of first derivative of data.
    
    This method uses Savitzky-Golay to approximate the first derivative of the 
    data given in one of the StaibDat class's default data arrays. Input 
    arguments as well as their default values are given as follows:
      key: A string indicating which of the object's data should be smoothed 
        (e.g. C1, C2).
      kernel: A positive integer giving the number of points the smoothing 
        algorithm should consider. Default = 13.
      order: A positive integer giving the order of the polynomial used in the 
        smoothing algorithm. Default = 3.
        
    The implementation of Savitzky-Golay was wholesale copied and slightly 
    modified from the SciPy cookbook: 
      http://www.scipy.org/Cookbook/SavitzkyGolay

    See the original Savitzky-Golay paper at DOI: 10.1021/ac60214a047
    """

    return self.__savitzky_golay(self[key],kernel,order,deriv = 1)

  def __savitzky_golay(self, data, kernel, order, deriv):
    """
    Return smooth or differentiated data according to the Savitzky-Golay 
    algorithm.
    
    The implementation of Savitzky-Golay was wholesale copied and slightly 
    modified from the SciPy cookbook: 
      http://www.scipy.org/Cookbook/SavitzkyGolay

    See the original Savitzky-Golay paper at DOI: 10.1021/ac60214a047
    """
    try:
      kernel = abs(int(kernel))
      order = abs(int(order))
    except ValueError, msg:
      raise ValueError("kernel and order have to be of type int (floats will be converted).")
    if kernel % 2 != 1 or kernel < 1:
      raise TypeError("kernel size must be a positive odd number, was: %d" % kernel)
    if kernel < order + 2:
      raise TypeError("kernel is to small for the polynomals\nshould be > order + 2")

    # a second order polynomal has 3 coefficients
    order_range = range(order+1)
    half_window = (kernel -1) // 2
    b = numpy.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    # since we don't want the derivative, else choose [1] or [2], respectively
    m = numpy.linalg.pinv(b).A[deriv]
    window_size = len(m)
    half_window = (window_size-1) // 2

    # precompute the offset values for better performance
    offsets = range(-half_window, half_window+1)
    offset_data = zip(offsets, m)

    smooth_data = list()

    # temporary data, with padded zeros (since we want the same length after smoothing)
    data = numpy.concatenate((numpy.zeros(half_window), data, numpy.zeros(half_window)))
    for i in range(half_window, len(data) - half_window):
      value = 0.0
      for offset, weight in offset_data:
        value += weight * data[i + offset]
      smooth_data.append(value)
    return numpy.array(smooth_data)




    def gaussian_fit(self, key, index1, index2, order, backgroundtype, fit_size):
    """
    This method returns an n-peak Gaussian fit in the form of a numpy array, along with some Gaussian-related statistics. 

    For a specified subset of the data, the outputs of this method are the median and standard deviation, sum of the least square errors (SSE), and the coefficient of determination (R^2) of the fitting. If there is more than one peak to be fitted, relative coefficients of each peak will also be returned. 

    The inputs and their defaults are:
       key: A string indicating which of the object's data should be analyzed (count data).
       index1: A positive integer that corresponds to the index of the first energy value that is greater than the lower bound of the energy range to be gaussian fitted.
       index2: A positive integer that corresponds to the index of the last energy value that is less than the upper bound of the energy range to be gaussian fitted.
       order: A positive integer telling how many peaks should compose the fit. Default value is 1.
       backgroundtype: A string indicating the background type to be removed.
       fit_size: A positive integer indicating the desired number of evenly spaced data points in the returned Gaussian fit.       

 
    """	
    pass


    def background(self, key, index1, index2, model):	
    """
    This method will return another numpy array that is the background due to scattered electrons. 
    
    Rather than being a subtraction method, this will give an array that when plotted, is the background of your spectrum. This array can be subtracted from your spectrum as a precedent to the integrate() and gaussian_fit() methods.

    The inputs are:
    key: A string indicating which of the object's data should be analyzed.
    index1: A positive integer that corresponds to the index of the first energy value that is greater than the lower bound of the energy range to be gaussian fitted.
       index2: A positive integer that corresponds to the index of the last energy value that is less than the upper bound of the energy range to be gaussian fitted.
    model: A string indicating what type of background algorithm to use. This may be either a linear background, Shirley type background, Tougaard type background, or blended Shirley type background.
    
    """
    pass	
	
	
    def integrate(self, abscissa, ordinate, index1, index2, backgroundtype, integralmethod, args): 
    """
    This method will allow you to calculate the area under a spectrum, along with statistics/parameters from integration. 

    The inputs are:
       abscissa: A string indicating which of the object's data will be the abscissa values (KE, BE).
       ordinate: A string indicating which of the object's data will be the ordinate values (count data).
       index1: A positive integer that corresponds to the index of the first energy value that is greater than the lower bound of the energy range to be integrated.
       index2: A positive integer that corresponds to the index of the last energy value that is less than the upper bound of the energy range to be integrated.	
       backgroundtype: A string indicating the background type to be removed.
       integralmethod: A string indicating method of integration (Simpson, etc). 
       args: Other arguments affecting the integration method.
    """
    pass