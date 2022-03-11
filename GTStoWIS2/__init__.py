

"""
  module to map WMO 386 defined Abbreviated Header Lines (AHL) to WIS topics.
  this module is installed with default table versions, which
  can be used directly, or overridden with TableDir argument to the constructor.

  usage:

  import GTStoWIS2

  
  topic_mapper = GTStoWIS2.GTStoWIS2()


  for ahl in [ 'IUPA54_LFPW_150000', 'A_ISID01LZIB190300_C_EDZW_20200619030401_18422777' ]:
      topic = topic_mapper.mapAHLtoTopic( ahl )
      print( 'ahl: %s, mapped to: %s' % ( ahl, topic ) )




"""
import json
import pkgutil
import os.path

__version__ = '0.0.3'

class GTStoWIS2():

    def _readTables(self):
        """
          read in the tables to support the translation.

          as per https://github.com/wmo-im/GTStoWIS2/issues/5 removing hours from topic tree.
          we don't ingest Tables C4 and C5, to which references from TableA have also been removed.
          
          merged TableA, TableB and TableC6
          harmonization for topic tree structure
        """

        for t in [ 'A', 'C1', 'CCCC']:
            f = self.tableDir + '/Table%s.json' % t
            with open( f, 'r',encoding="UTF-8" ) as m:
                if self.debug: print( 'reading %s' % f )
                exec( "self.table"+t+"=json.load(m)" )
            if self.dump:
               d = eval( "json.dumps(self.table"+t+", indent=2)" )
               print( "Table%s : %s" % (t, d ) )



    def __init__(self,tableDir=None,debug=False,dump_tables=False):
        """
             create an instance for parsing WMO-386 AHL's.

             tableDir - directory where all the tables are, by default use one included in package.  
             debug - prints some interim steps in applying the tables.
             dump_tables - shows how the tables were interpreted by GTStoWIS2.

        """
        # originally wanted separator to be programmable, but realized that / is used in the json
        # tables themselves, so cannot really be an argument. need to use / and replace for protocols
        # that use something else (like AMQP using . )
        self.separator='/'
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
            subtopic = country + self.separator + centre
            return subtopic
        else:
            country = ''
            centre = ''
            CC = CCCC[0:2]
            for c in self.tableC1:
                if "CC" in self.tableC1[c]:
                    if CC in self.tableC1[c]['CC']:
                        return self.tableC1[c]['topic'] + self.separator + CCCC
        return 'unknown'                 
    

    def _getSubtopicA1(self, myT1, myT2, myA1, myA2, myii, mytableA1):
        subTopicA1 = ""
        if mytableA1 == "C1":
            AA = myA1 + myA2
            if AA in self.tableC1.keys():
                subTopicA1_C1 = self.tableC1[AA]["topic"]
            subTopicA1 = self.tableA[myT1]['T2'][myT2] + self.separator + subTopicA1_C1
        else:
            if myT1 in [ 'I', 'J', 'K']:
                iiKey = ""
                TT = myT1 + myT2
                if TT in self.tableA[myT1]['A1'].keys():
                    if myA1 in self.tableA[myT1]['A1'][TT].keys():
                        if "ii" in self.tableA[myT1]['A1'][TT][myA1]:
                            iiKeyList = self.tableA[myT1]['A1'][TT][myA1]["ii"].keys()
                            for key in iiKeyList:
                                if int(myii) < int(key):
                                    if iiKey == "":
                                        iiKey = key
                                    else:
                                        if int(iiKey) > int(key):
                                            iiKey = key
                                if iiKey != "":
                                    subTopicA1 = self.tableA[myT1]['A1'][TT][myA1]["ii"][iiKey]
                        else:
                            subTopicA1 = self.tableA[myT1]['A1'][TT][myA1]
        return subTopicA1
    
    def mapAHLtoTopic(self,ahl):
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
        if self.debug: print("topic from tableA: %s" % topic )

        # get topic and subtopics
        subtopic_cccc = self._getSubtopic_CCCC(input_c)
        if self.debug: print("subtopic_CCCC: %s" % subtopic_cccc )

        subtopicT2 = ""
        subtopicA1 = ""
        subtopicA2 = ""
        topic = self.tableA[T1]["topic"]

        if T2 in self.tableA[T1]['T2'].keys():
            subtopicT2 = self.tableA[T1]['T2'][T2]
        if self.debug: print("subtopicT2: %s" % subtopicT2 )

        if self.tableA[T1]['A1'] == "C1":
            subtopicA1 = self._getSubtopicA1(T1, T2, A1, A2, ii, self.tableA[T1]['A1'])
        else:
            subtopicA1 = self._getSubtopicA1(T1, T2, A1, A2, ii, "")
        if self.debug: print("subtopicA1: %s" % subtopicA1 )
        
        if subtopicA1 != "":
            fulltopic = subtopic_cccc + self.separator + subtopicA1
        else:
            if subtopicT2 != "":
                fulltopic = subtopic_cccc + self.separator + subtopicT2
            else:
                fulltopic = subtopic_cccc + self.separator + topic

        # not used as A2 always ""
        #subtopicA2 = self._getSubtopicA2(A2, tableA[T1]['A2'])
        #if self.debug: print("subtopicA2: %s" % subtopicA2 )
        #if subtopicA2 != "":
        #    fulltopic = fulltopic + self.separator + subtopicA2

        if self.debug: print("fulltopic is: %s" % fulltopic )

        return fulltopic

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

        if T1 in [ 'L'  ]:
            return '.grib'

        if TT in [ 'XW' ]:
            return '.txt'

        if T1 in [ 'X' ]:
            return '.cap'

        if T1 in [ 'D', 'H', 'O', 'Y' ]:
            return '.grib'

        if T1 in [ 'E', 'L', 'M', 'P', 'Q', 'R' ]:
            return '.bin'

        return '.txt'         

    def mapAHLtoRelPath(self,ahl):
        """
          return complete relative path based on a traditional file name.
          append extension if necessary.
        """
        topic = self.mapAHLtoTopic( ahl )
        ext = self.mapAHLtoExtension( ahl )

        lext = len(ext)
        if ( ahl[-lext:] == ext ) or ( ahl[-lext] == '.' ): #there is another extension et already.
             fname = ahl
        else:
             fname = ahl + ext

        if os.sep != self.separator :
           topic = topic.replace( self.separator, os.sep )

        relpath = topic + os.sep + fname
        if self.debug: print("relpath is: %s" % relpath )

        return relpath


if __name__ == '__main__':
    # for AMQP topic separator is a period, rather than a slash, as in MQTT
    g=GTStoWIS2( debug=False, dump_tables=False )
  
    for ahl in [ 'IUPA54_LFPW_150000' , 'A_ISID01LZIB190300_C_EDZW_20200619030401_18422777', \
        'UACN10_CYXL_170329_8064d8dc1a1c71b014e0278b97e46187.txt' ]:

        topic=g.mapAHLtoTopic( ahl ).replace('/','.')
        relpath=g.mapAHLtoRelPath( ahl )
        print( 'input ahl=%s\n\tAMQP topic=%s\n\trelPath=%s' % ( ahl, topic, relpath ) )
