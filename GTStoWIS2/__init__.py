

"""
  module to map WMO 386 defined Abbreviated Header Lines (AHL) to WIS topics.
  this module is installed with default table versions, which
  can be used directly, or overridden with TableDir argument to the constructor.

  usage:

  import GTStoWIS2

  
  topic_mapper = GTStoWIS2.GTStoWIS2()


  for ahl in [ 'IUPA54_LFPW_150000', 'A_ISID01LZIB190300_C_EDZW_20200619030401_18422777' ]:
      topic = topic_mapper.mapAHLtoFullTopic( ahl )
      print( 'ahl: %s, mapped to: %s' % ( ahl, topic ) )




"""
from base64 import b64encode
import calendar
import datetime
from hashlib import sha512
import functools
import json
import pkgutil
import os
import os.path
import stat
import time

"""

time routines imported from Sarracenia

floating point is the python native date/time representation, as returned
by the os.stat and lstat routines, or time.time().

"""

def nowflt():
    """
       return a floating point representation of the current time.
    """
    return timestr2flt(nowstr())

def nowstr():
    """
       return a string representation of the current time.
    """
    return timeflt2str(time.time())

def v3timeflt2str(f):
    """
       convert the given floating point time to a string.
    """
    nsec = "{:.9g}".format(f % 1)[1:]
    return "{}{}".format(time.strftime("%Y%m%dT%H%M%S", time.gmtime(f)), nsec)

def timestr2flt(s):
    """
       convert the given string date/time to floating point. 
    """
    if s[8] == "T":
        s = s.replace('T', '')
    dt_tuple = int(s[0:4]), int(s[4:6]), int(s[6:8]), int(s[8:10]), int(
        s[10:12]), int(s[12:14])
    t = datetime.datetime(*dt_tuple, tzinfo=datetime.timezone.utc)
    return calendar.timegm(t.timetuple()) + float('0' + s[14:])

default_properties= { 
    'baseUrl':'file://',       # depends on many things...
    'topicPrefix': 'v03/post', # for AMQP would set to 'v03.post'
    'topicSeparator':'/',      # for AMQP would set to '.'
    'preserveTime': True,      # include atime/mtime?
    'preserveMode': True,      # include mode property?
    'inlineEncoding': 'utf-8', # or base64
    'inlineMax': 512           # maximum size of files to include in message body. 
} 

__version__ = '0.0.2'

class GTStoWIS2():

    def _readTables(self):
        """
          read in the tables to support the translation 
        """

        for t in [ 'A', 'B', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C6', 'C7', 'CCCC', 'GISC'  ]:
            f = self.tableDir + '/Table%s.json' % t
            with open( f, 'r' ) as m:
                if self.debug: print( 'reading %s' % f )
                exec( "self.table"+t+"=json.load(m)" )
            if self.dump:
               d = eval( "json.dumps(self.table"+t+", indent=2)" )
               print( "Table%s : %s" % (t, d ) )


    def __init__(self,tableDir=None,debug=False,dump_tables=False, \
        properties=default_properties ):
        """
             create an instance for parsing WMO-386 AHL's.

             tableDir - directory where all the tables are, by default use one included in package.  
             debug - prints some interim steps in applying the tables.
             dump_tables - shows how the tables were interpreted by GTStoWIS2.

        """
        self.properties = properties
        self.debug=debug
        self.dump=dump_tables

        if tableDir is None:
            self.tableDir = os.path.dirname( __file__ )
            if not self.tableDir:
               self.tableDir = os.getcwd()
        else:
            self.tableDir = tableDir

        if self.debug: print( 'self.tableDir = %s' % self.tableDir )
        self._readTables()

    # get CCCC subtopic
    def _getSubtopic_CCCC(self, CCCC):
        if CCCC in self.tableCCCC.keys():
            country = self.tableCCCC[CCCC]["country_short"]
            centre = self.tableCCCC[CCCC]["centre"]
            subtopic = country + '/' + centre
            return subtopic
        else:
            country = ''
            centre = ''
            CC = CCCC[0:2]
            for c in self.tableC1:
                if "CC" in self.tableC1[c]:
                    if CC in self.tableC1[c]['CC']:
                        return self.tableC1[c]['topic'] + '/' + CCCC
        return 'unknown'                 
    

    def _getSubtopicTableT2(self, myT1, myT2, myA1, myii, mytableT2):
        subTopicT2 = ""
        if "B" in mytableT2:
            #print("tableT2 = B")
            keyList = self.tableB[myT1].keys()
            #print(keyList)
            if myT2 in keyList:
                subTopicT2 = self.tableB[myT1][myT2]
        else:
            if "C7" in mytableT2:
                #print("tableT2 = C7")
                TTA = myT1 + myT2 + myA1
                if TTA in self.tableC7.keys():
                    if "ii" in self.tableC7[TTA]:
                        iiKey = ""
                        iiKeyList = self.tableC7[TTA]["ii"].keys()
                        for key in iiKeyList:
                            if int(myii) < int(key):
                                if iiKey == "":
                                    iiKey = key
                                else:
                                    if int(iiKey) > int(key):
                                        iiKey = key
                        if iiKey != "":
                            subTopicT2 = self.tableC7[TTA]["ii"][iiKeys[count-1]]
                    else:
                        subTopicT2 = self.tableC7[TTA]
        return subTopicT2

    def _getSubtopicTableA1(self, myT1, myT2, myA1, myA2, myii, mytableA1):
        subTopicA1 = ""
        if mytableA1 == "C1":
            AA = myA1 + myA2
            if AA in self.tableC1.keys():
                subTopicA1 = self.tableC1[AA]["topic"]
        else:
            if mytableA1 == "C3":
                subTopicA1 = self.tableC3[myA1]
            else:
                if mytableA1 == "C6":
                    iiKey = ""
                    TT = myT1 + myT2
                    if TT in self.tableC6.keys():
                        if myA1 in self.tableC6[TT].keys():
                            if "ii" in self.tableC6[TT][myA1]:
                                iiKeyList = self.tableC6[TT][myA1]["ii"].keys()
                                for key in iiKeyList:
                                    if int(myii) < int(key):
                                        if iiKey == "":
                                            iiKey = key
                                        else:
                                            if int(iiKey) > int(key):
                                                iiKey = key
                                if iiKey != "":
                                    subTopicA1 = self.tableC6[TT][myA1]["ii"][iiKey]
                            else:
                                subTopicA1 = self.tableC6[TT][myA1]
                        else:
                            if "A-Z" in self.tableC6[TT].keys():
                                subTopicA1 =  self.tableC6[TT]["A-Z"]
        return subTopicA1
    
    def _getSubtopicTableA2(self, myA2, mytableA2):
        subTopicA2 = ""
        if mytableA2 == "C4":
            subTopicA2 = self.tableC4[myA2]
        else:
            if mytableA2 == "C3":
                subTopicA2 = self.tableC3[myA2]
            else:
                if mytableA2 == "C5":
                    if myA2 in self.tableC5.keys():
                        subTopicA2 = self.tableC5[myA2]
        return subTopicA2
    
    def mapAHLtoSubTopic(self,ahl):
        """
        Returns a topic, given an ahl... actually a file name that contains an ahl.

          filename formats...

          fn386 : A_ISID01LZIB190300_C_EDZW_20200619030401_18422777
            cdn : IUPA54_LFPW_150000
        
        The routine looks for the A_ at the beginning to decide how to interpret the ahl.

        """
        if self.debug: print("input ahl=%s" % ahl )
        fn386=False
        if ahl[0:2] == 'A_':
           ahl=ahl[2:]
           fn386=True

        # split input TTAAii
        T1 = ahl[0:1]
        T2 = ahl[1:2]
        A1 = ahl[2:3]
        A2 = ahl[3:4]
        ii = ahl[4:6]

        if fn386:
            input_c = ahl[6:10]
        else:
            input_c = ahl[7:11]

        if self.debug: print( "T1=%s, T2=%s, A1=%s, A2=%s, ii=%s, CCCC=%s" % ( T1, T2, A1, A2, ii, input_c ) )

        # get WMOtables for T1
        tableT2 = self.tableA[T1]["T2"]
        tableA1 = self.tableA[T1]["A1"]
        tableA2 = self.tableA[T1]["A2"]
        topic = self.tableA[T1]["topic"]

        if self.debug: print("topic from tableA: %s" % topic )

        # get topic and subtopics
        subtopic_cccc = self._getSubtopic_CCCC(input_c)
        if self.debug: print("subtopic_CCCC: %s" % subtopic_cccc )

        subtopicT2 = ""
        subtopicA1 = ""
        subtopicA2 = ""
        fulltopic = subtopic_cccc + '/' + topic

        subtopicT2 = self._getSubtopicTableT2(T1, T2, A1, ii, tableT2)
        if self.debug: print("subtopicT2: %s" % subtopicT2 )
        if subtopicT2 != "":
            fulltopic = fulltopic + '/' + subtopicT2

        subtopicA1 = self._getSubtopicTableA1(T1, T2, A1, A2, ii, tableA1)
        if self.debug: print("subtopicA1: %s" % subtopicA1 )
        if subtopicA1 != "":
            fulltopic = fulltopic + '/' + subtopicA1

        subtopicA2 = self._getSubtopicTableA2(A2, tableA2)
        if self.debug: print("subtopicA2: %s" % subtopicA2 )
        if subtopicA2 != "":
            fulltopic = fulltopic + '/' + subtopicA2

        if self.properties[ 'topicSeparator' ] != '/' :
           fulltopic = fulltopic.replace( '/', self.properties[ 'topicSeparator' ] )

        if self.debug: print("fulltopic is: %s" % fulltopic )

        return fulltopic


    def mapAHLtoFullTopic( self, ahl ):
        return self.properties['topicPrefix'] + '/' + self.mapAHLtoSubTopic( ahl )

    def mapAHLtoExtension(self,ahl):
        """        
        return an appropriate file extension for a file.

        """        
        if self.debug: print("input ahl=%s" % ahl )
        fn386=False
        if ahl[0:2] == 'A_':
           ahl=ahl[2:]
           fn386=True

        T1 = ahl[0:1]
        TT = ahl[0:2] 

        if T1 in [ 'G' ]:
            return '.grid'

        if T1 in [ 'I' ]:
            return '.bufr'

        if TT in [ 'IX' ]:
            return '.hdf'

        if T1 in [ 'K' ]:
            return '.crex'

        if TT in [ 'LT' ]: 
            return '.iwxxm'

        if T1 in [ 'L' ]:
            return '.grib'

        if TT in [ 'XW' ]:
            return '.txt'

        if T1 in [ 'X' ]:
            return '.cap'

        if T1 in [ 'D', 'H', 'O', 'Y' ]:
            return '.grib'

        if T1 in [ 'E', 'P', 'Q', 'R' ]:
            return '.bin'

        return '.txt'         

    def mapAHLtoRelPath(self,ahl):
        """
          return complete relative path based on a traditional file name.
          append extension if necessary.
        """
        topic = self.mapAHLtoSubTopic( ahl )
        ext = self.mapAHLtoExtension( ahl )

        lext = len(ext)
        if ( ahl[-lext:] == ext ) or ( ahl[-lext] == '.' ): #there is another extension et already.
             fname = ahl
        else:
             fname = ahl + ext

        if os.sep != '/' :
           topic = topic.replace( '/', os.sep )

        relpath = topic + os.sep + fname
        if self.debug: print("relpath is: %s" % relpath )

        return relpath

    def mapAHLtoMessage(self, ahl, path):
       """
           given an ahl, and a corresponding file, build an MQP message as a python dictionary
           which can be turned into json using: json.dumps(msg)
       """
       m = {}
       m[ 'baseUrl' ] = self.properties[ 'baseUrl' ] 
       m[ 'relPath' ] = self.mapAHLtoRelPath( ahl )
       m[ 'pubTime' ] = v3timeflt2str(time.time())

       lstat = os.lstat( path )

       # WARNING: this checksum calculation might be wrong. It looks OK, but have not validated it.
       h=sha512()
       if lstat.st_size < self.properties['inlineMax'] :
         # FIXME: should have guessing logic here to pick utf-8 if it makes sense.
         #        and back off to base64 otherwise.
         m[ 'content' ] = { 'encoding': self.properties['inlineEncoding'], 'value':'' }
           
       with open(path, 'rb') as f:
            for data in iter(functools.partial(f.read, 1024 * 1024), b''):
                if lstat.st_size < self.properties['inlineMax'] :
                   if self.properties['inlineEncoding'] == 'utf-8':
                       m['content']['value'] += data.decode('utf-8')
                   else:
                       m['content']['value'] += b64encode(data).decode('utf-8')

                h.update(data)

       m[ 'integrity' ]  = { 'method': 'sha512', 'value':b64encode(h.digest()).decode('utf-8') }

       if self.properties[ 'preserveTime' ]:
           m['mtime'] = v3timeflt2str(lstat.st_mtime)
           m['atime'] = v3timeflt2str(lstat.st_atime)

       if self.properties[ 'preserveMode' ]:
           m['mode'] = "%o" % (lstat[stat.ST_MODE] & 0o7777)
       return m


if __name__ == '__main__':
    # for AMQP topic separator is a period, rather than a slash, as in MQTT
    g=GTStoWIS2( debug=False, dump_tables=False )
  
    for ahl in [ 'IUPA54_LFPW_150000' , 'A_ISID01LZIB190300_C_EDZW_20200619030401_18422777', \
        'UACN10_CYXL_170329_8064d8dc1a1c71b014e0278b97e46187.txt' ]:

        topic=g.mapAHLtoFullTopic( ahl ).replace('/','.')
        relpath=g.mapAHLtoRelPath( ahl )
        print( 'input ahl=%s\n\tAMQP topic=%s\n\trelPath=%s' % ( ahl, topic, relpath ) )

    import json

    dataDir='../sample_GTS_data'

    for path in os.listdir( dataDir ):
        print( 'path: %s' % path )
        m= g.mapAHLtoMessage( path, dataDir + os.sep + path )
        msg = json.dumps(m)
        print( 'message is: %s' % msg )


