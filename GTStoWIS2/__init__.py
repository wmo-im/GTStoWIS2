#!/usr/bin/python3

"""
  module to map WMO 386 defined Abbreviated Header Lines to WIS topics.
  this module is installed with default table versions, which
  can be used directly, or overridden with TableDir argument to the constructor.

  usage:


"""
import json
import pycountry
import pkgutil
import os.path

class GTStoWIS2(): 

    def _skip_line(self,l):
        if l[0] == '#':
           return True
        if len(l) < 4 :
           return True
        return False

    def _parseCSV(self, tid, word=True ):
        exec( "self.table" + tid + " = {}" )
        with open( self.tableDir + '/Table'+tid+'.csv', 'r' ) as m:
            for l in m.readlines():
                if self._skip_line(l):
                    continue
                b = l.split(',')
                exec( "self.table" + tid + "[b[0]] = b[1:]" )
                if self.dump:
                   exec( "print( '\tTable"+tid+"[%s]=%s' % ( b[0], self.table" + tid + "[b[0]] ))" )


    def _parseCSVB(self, tid, word=True ):
        exec( "self.table" + tid + " = {}" )
        with open( self.tableDir + '/Table'+tid+'.csv', 'r' ) as m:
            for l in m.readlines():
                if self._skip_line(l):
                    continue
                b = l.split(',')
                for i in b[0]:
                    j=i+b[1]
                    exec( "self.table" + tid + "[j] = b[2:]" ) 
                    if self.dump:
                        exec( "print('\tTable" + tid + "[ %s ]= %s' % (j,self.table" + tid +"[j]))" )

    def _readTables(self):

        # TableA
        self.tableA={}
        self.tableC1={}
        with open( self.tableDir + '/TableA.json', 'r' ) as m:
          self.tableA=json.load(m)
        with open( self.tableDir + '/TableC1.json', 'r' ) as m:
          self.tableC1=json.load(m)

        with open( self.tableDir + '/TableCCCC.json', 'r' ) as m:
          self.tableCCCC=json.load(m)

        if self.dump:
            print( "Table A: %s" % json.dumps(self.tableA, indent=2) )
            print( "Table C1: %s" % json.dumps(self.tableC1, indent=2) )
            print( "Table CCCC: %s" % json.dumps(self.tableC1, indent=2) )

        # TableB
        for t in [ 'B', 'C4', 'D2' ]:
            self._parseCSVB(t)

        for t in [ 'C2', 'C3', 'C5', 'C6', 'D1', 'D3' ]:
            self._parseCSV(t)

    """

    """
    def __init__(self,tableDir=None,debug=False,dump_tables=False):
          
        if tableDir == None:
            self.tableDir = os.path.dirname( __file__ )
        else:
            self.tableDir = tableDir
        self.debug=debug
        self.dump=dump_tables
        self._readTables()
        c = list(map( lambda x : x.alpha_2.lower(), pycountry.countries))
        c.sort()

        self.iso2countries = c
        if self.dump:
            print( "iso2countries: %s" % c )
        
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
           
    def _USAA(self,AA):   # American local bulletins use AA for more local meanings: US States, and neighbouring Countries.
        if AA == 'CN': return 'ca'
        elif AA == 'SV': return 'vg'
        else: return 'us'


    def AATopic(self,TT,AA,CCCC,ahlHint):
        topic=""
        if self.debug:
           print( "AATopic 1 input: TT=%s, AA=%s, ahlHint=%s" % ( TT, AA, ahlHint) )
        if "AA" in ahlHint:
            atab = ahlHint["AA"]

            if ( TT in [ 'SF', 'SR', 'SX' ] ) and ( CCCC in [ 'KWAL' ] ):  
                # Americans have some by state: SROK... OK-Oklahoma
                # note use CCCC because CA... ( Carribbean or California?) how to know?
                topic=self._USAA(AA)  # losing the sub-national info...
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
                if self.debug:
                    print( "AATopic 2 self._AATopic=self.table"+atab+"[\""+AA+"\"][0]" )
                exec( "self._AATopic=self.table"+atab+"[\""+AA+"\"][0]" )
                topic=self._AATopic
        elif "A1" in ahlHint:
            a1 = ahlHint["A1"]
            a2 = ahlHint["A2"]
            if ( TT in [ 'TR', 'TH'] ) and ( CCCC in [ 'KWBC' ] ): 
                self.a1topic=self._USAA(AA) 
            elif a1 == 'C6' :
                i=TT+AA[0]
                if self.debug: print( "AATopic 3 self.a1topic=self.table"+a1+"[%s][0]" % i )
                exec( "self.a1topic=self.table"+a1+"[i][0]" )
                if self.debug: print( "self.a1topic=%s" % self.a1topic )
                
                if a2 == 'C3':
                    self.a2topic=self.tableC3[AA[1]][0]
                    if self.debug: print( "AATopic 4 self.a2topic=self.tableC3[%s]=%s" % (AA[1], self.a2topic) )
                else: #C4
                    j=TT[0]+AA[0]
                    self.a2topic=self.tableC4[j][0]
                    if self.debug: print( "AATopic 5 self.a2topic=self.tableC4[%s]=%s" % (j, self.a2topic) )
            else: 
                if (a1 == 'C3') or ( TT in [ 'UB' ]):
                    self.a1topic=self.tableC3[AA[1]][0]
                    if self.debug: print( "AATopic 6 self.a1topic=self.tableC3[%s][0] = %s" % (AA[1],self.a1topic) )
                else:
                    if self.debug: print( "AATopic 7 self.a1topic=self.table"+a1+"[%s][0]" % (AA) )
                    exec( "self.a1topic=self.table"+a1+"[AA][0]" )

                    exec( "self.a2topic=self.table"+a2+"[AA][0]" )
                    if self.debug: print( "AATopic 8 self.a2topic=self.table"+a2+"[AA][0] = %s" % ( self.a2topic ) )

            if self.a1topic  != "":
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
        if self.debug: print( "topic from CCCC is: %s " % CCCCTopic )
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
           if self.debug: print( "ahlpib: %s" % ahlpiB )
           TTTopic=ahlpiB[0]

        topic=TTTopic
        if self.debug: print( "topic from TT/B is: %s " % TTTopic )

        AATopic=self.AATopic(TT,AA,CCCC,ahlParseHint) 
        if AATopic :
           topic += '/' + AATopic

        # If CCCC not in the original table, use AA to assign a country.
        if not CCCC in self.tableCCCC and AATopic in self.iso2countries:
           CCCCTopic = AATopic + '/' + CCCC
           if self.debug: print( "topic from CCCC revised to: %s " % CCCCTopic )

        if self.debug: print( "topic from AA/C is: %s " % AATopic )

        iiTopic=self.iiTopic(T1,T2,AA[1],ii,ahlParseHint)
        if iiTopic :
           topic += '/' + iiTopic

        if CCCCTopic:
           topic = CCCCTopic + '/' + topic

        if self.debug: 
            print( "topic from ii/C is: %s " % iiTopic )
            print( "topic is: %s " % topic )

        return topic
        
    def mapTopicToAHL(self,topic):
        print( "NotImplemented" )
