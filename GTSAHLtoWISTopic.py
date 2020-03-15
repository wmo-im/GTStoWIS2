#!/usr/bin/python3

"""
  module to map WMO 386 defined Abbreviated Header Lines to WIS topics.
  this module is installed with default table versions, which
  can be used directly, or overridden with TableDir argument to the constructor.

  usage:


"""
import json

#dump tables on startup.
dump=False

debug=False
debug=True

class GTSAHLtoWISTopicMapper(): 

    def skip_line(self,l):
        if l[0] == '#':
           return True
        if len(l) < 4 :
           return True
        return False

    def parseCSV(self, tid, word=True ):
        exec( "self.table" + tid + " = {}" )
        with open( self.tableDir + '/Table'+tid+'.csv', 'r' ) as m:
            for l in m.readlines():
                if self.skip_line(l):
                    continue
                b = l.split(',')
                exec( "self.table" + tid + "[b[0]] = b[1:]" )
                if dump:
                   exec( "print( '\tTable"+tid+"[%s]=%s' % ( b[0], self.table" + tid + "[b[0]] ))" )


    def parseCSVB(self, tid, word=True ):
        exec( "self.table" + tid + " = {}" )
        with open( self.tableDir + '/Table'+tid+'.csv', 'r' ) as m:
            for l in m.readlines():
                if self.skip_line(l):
                    continue
                b = l.split(',')
                for i in b[0]:
                    j=i+b[1]
                    exec( "self.table" + tid + "[j] = b[2:]" ) 
                    if dump:
                        exec( "print('\tTable" + tid + "[ %s ]= %s' % (j,self.table" + tid +"[j]))" )

    def readTables(self):

        # TableA
        self.tableA={}
        self.tableC1={}
        with open( self.tableDir + '/TableA.json', 'r' ) as m:
          self.tableA=json.load(m)
        with open( self.tableDir + '/TableC1.json', 'r' ) as m:
          self.tableC1=json.load(m)

        with open( self.tableDir + '/CCCC_to_WIS_Centre.json', 'r' ) as m:
          self.tableCCCC=json.load(m)

        if dump:
            print( "Table A: %s" % json.dumps(self.tableA, indent=2) )
            print( "Table C1: %s" % json.dumps(self.tableC1, indent=2) )
            print( "Table CCCC: %s" % json.dumps(self.tableC1, indent=2) )

        # TableB
        for t in [ 'B', 'C4', 'D2' ]:
            self.parseCSVB(t)

        for t in [ 'C2', 'C3', 'C5', 'C6', 'D1', 'D3' ]:
            self.parseCSV(t)


    def __init__(self,tableDir=None):
          
        self.tableDir = tableDir
        self.readTables()
        
    def iiTopic(self,t1,t2,a2,ii,ahlHint):

        try:
            inum=int(ii)
        except:
            return("")

        if inum==0: return ""

        if t1 == 'O':
           if ii in self.tableD1:
              return(self.tableD1[ii])
           else:
              return( "undefined depth" )
        #manual implementation of D3
        elif t1 == 'F' and t2 == 'A':
           if inum < 49 :
                return "air/navigation/alerts/area" 
           return "air/navigation"
        elif t1 == 'U' and t2 == 'A':
           if inum < 60 :
                return "air/navigation/routine" 
           elif inum < 70:
                return "air/navigation/special" 
           elif inum < 80:
                return "air/navigation/special/ash" 
           else:
                return "air/navigation/reserved" 

        if 'D' in ahlHint['ii']:
            if ahlHint['ii'] == 'D2':
               k=a2+ii
               if k in self.tableD2:
                  return(self.tableD2[k][0])
               else:
                  return "" 
        return "" 
           
    def USAA(self,AA):   # American local bulletins use AA for more local meanings: US States, and neighbouring Countries.
        if AA == 'CN': return 'ca'
        elif AA == 'SV': return 'vg'
        else: return 'us'


    def AATopic(self,TT,AA,CCCC,ahlHint):
        topic=""
        if debug:
           print( "AATopic input: TT=%s, AA=%s, ahlHint=%s" % ( TT, AA, ahlHint) )
        if "AA" in ahlHint:
            atab = ahlHint["AA"]

            if ( TT in [ 'SF', 'SR', 'SX' ] ) and ( CCCC in [ 'KWAL' ] ):  
                # Americans have some by state: SROK... OK-Oklahoma
                # note use CCCC because CA... ( Carribbean or California?) how to know?
                topic=self.USAA(AA)  # losing the sub-national info...
            elif TT[0] == 'S' and AA[0] in [ 'W', 'V', 'F' ]:
                if TT == 'SO' and AA[0] in [ 'F' ]: suffix='buoy'
                if AA[0] == 'W' : suffix='station'
                if AA[0] == 'V' : suffix='ship'
                else: suffix='surface'

                if AA[1] in self.tableC2:
                    topic=self.tableC2[AA[1]][0]+'/'+suffix
                else:
                    topic=self.tableC1[AA][0]+'/'+suffix
            else: 
                if debug:
                    print( "self._AATopic=self.table"+atab+"[\""+AA+"\"][0]" )
                exec( "self._AATopic=self.table"+atab+"[\""+AA+"\"][0]" )
                topic=self._AATopic
        elif "A1" in ahlHint:
            a1 = ahlHint["A1"]
            a2 = ahlHint["A2"]
            if ( TT in [ 'TR', 'TH'] ) and ( CCCC in [ 'KWBC' ] ): 
                topic=self.USAA(AA) 
            elif a1 == 'C6' :
                i=TT+AA[0]
                if debug: print( "self.a1topic=self.table"+a1+"[%s][0]" % i )
                exec( "self.a1topic=self.table"+a1+"[i][0]" )
                if debug: print( "self.a1topic=%s" % self.a1topic )
                
                if a2 == 'C3':
                    self.a2topic=self.tableC3[AA[1]][0]
                    if debug: print( "self.a2topic=self.tableC3[%s]=%s" % (AA[1], self.a2topic) )
                else: #C4
                    j=TT[0]+AA[0]
                    self.a2topic=self.tableC4[j][0]
                    if debug: print( "self.a2topic=self.tableC4[%s]=%s" % (j, self.a2topic) )
            else: 
                if (a1 == 'C3') or ( TT in [ 'UB' ]):
                    self.a1topic=self.tableC3[AA[1]][0]
                    print( "self.a1topic=self.tableC3[%s][0] = %s" % (AA[1],self.a1topic) )
                else:
                    print( "self.a1topic=self.table"+a1+"[%s][0]" % (AA) )
                    exec( "self.a1topic=self.table"+a1+"[AA][0]" )

                    exec( "self.a2topic=self.table"+a2+"[AA][0]" )
                    if debug: print( "self.a2topic=self.table"+a2+"[AA][0] = %s" % ( self.a2topic ) )

            if topic  != "":
                if self.a2topic != "": 
                   topic = self.a1topic + "/" + self.a2topic
            elif hasattr(self,'a2topic') and self.a2topic != "":
                   topic = self.a2topic 
        return topic 

    """
        return the toppic hierarchy for a given AHL
    """

    def mapAHLtoTopic(self,ahl):
        TT=ahl[0:2].upper()
        AA=ahl[2:4].upper()
        ii=ahl[4:6]
        T1=ahl[0].upper()
        T2=ahl[1].upper()
        CCCC = ahl[7:11]
        if CCCC in self.tableCCCC:
            CCCCTopic=self.tableCCCC[ CCCC ]["centre"]
        else:
            CCCCTopic=CCCC
        if debug: print( "topic from CCCC is: %s " % CCCCTopic )
        ahlParseHint=self.tableA[ T1 ]

        if T1 == 'K':
           print( 'CREX Table C7 not yet implemented')
           TTTopic="crex"
        elif TT == 'SZ':
           print( 'TT=SZ not implemented yet.' )
           TTTopic="sea/"
        elif T1 == 'B': # Addressed messages, no idea...
           return CCCCTopic + "/addressed"
        else:
           ahlpiB=self.tableB[ TT ]
           if debug: print( "ahlpib: %s" % ahlpiB )
           TTTopic=ahlpiB[0]

        topic=TTTopic
        if debug: print( "topic from TT/B is: %s " % TTTopic )

        AATopic=self.AATopic(TT,AA,CCCC,ahlParseHint) 
        if AATopic :
           topic += '/' + AATopic
        if debug: print( "topic from AA/C is: %s " % AATopic )

        iiTopic=self.iiTopic(T1,T2,AA[1],ii,ahlParseHint)
        if iiTopic :
           topic += '/' + iiTopic

        if CCCCTopic:
           topic = CCCCTopic + '/' + topic

        if debug: print( "topic from ii/C is: %s " % iiTopic )
        if debug: print( "topic is: %s " % topic )
        return topic
        
    def mapTopicToAHL(self,topic):
        print( "NotImplemented" )
        pas

"""
The following logic is used as a test harness when developing plugins.
Append this file to the end of the plugin, and  then invoke it from
the command line.  Add variables to parent (in the testmessage class) 
as needed to exercise your plugin.

"""

if __name__ == '__main__':

  topic_builder=GTSAHLtoWISTopicMapper(".")


  ahl="SACN37 CWAO 090807"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "ahl=%s, topic=%s\n" % ( ahl, t ) )

  ahl="SSAS33 KWBC 14220"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "ahl=%s, topic=%s\n" % ( ahl, t ) )

  ahl="SNFI01 KWBC 142200"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "ahl=%s, topic=%s\n" % ( ahl, t ) )

  ahl="IUPA54_LFPW_150000"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "ahl=%s, topic=%s\n" % ( ahl, t ) )

  ahl="IUPD48_SOWR_150004"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )


  ahl="FTPA32_KWBC_151015_AAA"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SRFL20_KWAL_151016"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SXWY50_KWAL_151017"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SNVB21_AMMC_151000"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SROK30_KWAL_151111"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SXNE55_KWAL_151116"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="UANT01_CWAO_15111"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="NXUS60_PHFO_151120"  # PHFO not in WMO CCCC Table... Honolulu forecast office.
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SRWV30_KWAL_151120_"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="FTZZ40_KAWN_151121"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="SZMS01_WMKK_151123"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )

  ahl="UBUS31_KWBC_151125"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="TRCA01_KWBC_151000"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="THCA01_KWBC_151100"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="IUSV51_KWBC_151150"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="IUSV52_KWBC_151150"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="SRUS54_KOHX_151216"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="CXUS43_KBIS_151217"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="NZUS93_KARX_151217"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="YVXX84_KAWN_151200"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="SFTX57_KWAL_151220"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="BMBB91_KJAX_151224"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="IUSZ52_KWBC_151235"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="INGX27_KNES_151252"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="UBFL90_KWBC_151310"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="USBZ05_SBBR_151200"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="HEPF98_KWBC_151800"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
  ahl="HGJF98_KWBC_151800"
  print( "ahl=%s" % ( ahl ) )
  t = topic_builder.mapAHLtoTopic(ahl)
  print( "topic=%s\n" % ( t ) )
  
