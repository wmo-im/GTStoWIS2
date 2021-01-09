

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


    def __init__(self,tableDir=None,debug=False,dump_tables=False,separator='/'):
        """
             create an instance for parsing WMO-386 AHL's.

             tableDir - directory where all the tables are, by default use one included in package.  
             debug - prints some interim steps in applying the tables.
             dump_tables - shows how the tables were interpreted by GTStoWIS2.

        """
        self.separator=separator
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
        fulltopic = subtopic_cccc + self.separator + topic

        subtopicT2 = self._getSubtopicTableT2(T1, T2, A1, ii, tableT2)
        if self.debug: print("subtopicT2: %s" % subtopicT2 )
        if subtopicT2 != "":
            fulltopic = fulltopic + self.separator + subtopicT2

        subtopicA1 = self._getSubtopicTableA1(T1, T2, A1, A2, ii, tableA1)
        if self.debug: print("subtopicA1: %s" % subtopicA1 )
        if subtopicA1 != "":
            fulltopic = fulltopic + self.separator + subtopicA1

        subtopicA2 = self._getSubtopicTableA2(A2, tableA2)
        if self.debug: print("subtopicA2: %s" % subtopicA2 )
        if subtopicA2 != "":
            fulltopic = fulltopic + self.separator + subtopicA2

        if self.debug: print("fulltopic is: %s" % fulltopic )

        return fulltopic

    def mapTopicToAHL(self,topic):
        print( "NotImplemented" )


       


if __name__ == '__main__':
    g=GTStoWIS2( debug=True, dump_tables=False )
    g.mapAHLtoTopic( 'IUPA54_LFPW_150000' )
    g.mapAHLtoTopic( 'A_ISID01LZIB190300_C_EDZW_20200619030401_18422777' )
    g.mapAHLtoTopic( 'UACN10_CYXL_170329_8064d8dc1a1c71b014e0278b97e46187.txt' )
