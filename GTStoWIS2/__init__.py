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

__version__ = '0.0.1'

class GTStoWIS2(): 


    sep='/'

    def _skip_line(self,l):
        if l[0] == '#':
           return True
        if len(l) < 4 :
           return True
        return False

    def _parseCSV(self, tid, word=True ):
        t=self.tableDir + os.sep + 'Table'+tid+'.csv'
        if self.debug: print( "reading %s " % t )
        exec( "self.table" + tid + " = {}" )
        with open( t, 'r' ) as m:
            for l in m.readlines():
                if self._skip_line(l):
                    continue
                b = l.split(',')
                exec( "self.table" + tid + "[b[0]] = b[1:]" )
                if self.dump:
                   exec( "print( '\tTable"+tid+"[%s]=%s' % ( b[0], self.table" + tid + "[b[0]] ))" )


    def _parseCSVB(self, tid, word=True ):
        t= self.tableDir + os.sep + 'Table'+tid+'.csv'
        if self.debug: print( "reading %s " % t )
        exec( "self.table" + tid + " = {}" )
        with open( t, 'r' ) as m:
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

        for t in [ 'A', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'CCCC', 'GISC' ]:
            f = self.tableDir + '/Table%s.json' % t
            with open( f, 'r' ) as m:
                if self.debug: print( 'reading %s' % f )
                exec( "self.table"+t+"=json.load(m)" )
            if self.dump:
               d = eval( "json.dumps(self.table"+t+", indent=2)" )
               print( "Table%s : %s" % (t, d ) ) 

        # TableB
        for t in [ 'B', 'D2' ]:
            self._parseCSVB(t)

        for t in [ 'D1', 'D3' ]:
            if self.debug: print( 'reading Table%s' % t )
            self._parseCSV(t)

    """

    """
    def __init__(self,tableDir=None,debug=False,dump_tables=False):
        """
             create an instance for parsing WMO-386 AHL's.

             tableDir - directory where all the tables are, by default use one included in package.  
             debug - prints some interim steps in applying the tables.
             dump_tables - shows how the tables were interpreted by GTStoWIS2.

        """
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
        
    def __iiTopic(self,t1,t2,a2,ii,ahlHint):

        try:
            inum=int(ii)
        except:
            return("")

        if inum==0: return ""

        if t1 == 'O':
           if ii in self.tableD1:
              #decided all TableD2 entries should land in same topic.
              #return(self.tableD1[ii])
              return('')
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
                  #decided all TableD2 entries should land in same topic.
                  #return(self.tableD2[k][0])
                  return ''
               else:
                  return ''
        return '' 
           
    def _USAA(self,AA):   
        """ 
              Some American bulletins, from KWAL mostly, use AA for more local meanings: US States, and neighbouring Countries.
              CA - California? OK- Oklahoma, FL-FLorida, etc...
    
              CN - Canada, MX - Mexico...  
              BZ ? guessing Belize, C1 would say Brazil... used Brasil
              Do not know about these:  CL, FR, SK, SV, VX, XX, 
        """
        if AA == 'CN': return 'ca'
        if AA == 'MX': return 'mx'
        if AA == 'SV': return 'vg'
        if AA == 'BZ': return 'br'
        if AA == 'CH': return 'cl'
        if AA == 'FR': return 'fr'
        if AA == 'NL': return 'nl'
        else: return 'us'


    def __AATopic(self,TT,AA,ii,CCCC,ahlHint):
        topic=""
        self.a1topic=""
        self.a2topic=""
        if self.debug:
           print( "AATopic 1 input: TT=%s, AA=%s, ahlHint=%s" % ( TT, AA, ahlHint) )
        if "AA" in ahlHint:
            atab = ahlHint["AA"]

            if ( ( TT in [ 'SF', 'SR', 'SX' ] ) and ( CCCC in [ 'KWAL' ] ) ) or \
               ( ( TT in [ 'UB' ] ) and ( CCCC in [ 'KWBC' ] ) ):  
                # Americans have some by state: SROK... OK-Oklahoma
                # note use CCCC because CA... ( Carribbean or California?) how to know?
                topic=self._USAA(AA)  # losing the sub-national info...
            elif ( TT[0] == 'S' ) and (AA[0] in [ 'W', 'V', 'F' ]):
                if TT == 'SO' and AA[0] in [ 'F' ]: suffix='buoy'
                if AA[0] == 'W' : suffix='station'
                if AA[0] == 'V' : suffix='ship'
                else: suffix='surface'

                if AA[1] in self.tableC2:
                    topic=self.tableC2[AA[1]]+GTStoWIS2.sep+suffix
                else:
                    topic=self.tableC1[AA]['topic']+ GTStoWIS2.sep +suffix
            else: 
                if atab == 'C1': idx='["topic"]'
                else: idx='[0]'
                if self.debug:
                    print( "AATopic 2 self._AATopic=self.table"+atab+"[\""+AA+"\"]"+idx )
                exec( "self._AATopic=self.table"+atab+"[\""+AA+"\"]"+idx )
                topic=self._AATopic
        elif "A1" in ahlHint:
            a1 = ahlHint["A1"]
            a2 = ahlHint["A2"]
            #if ( TT in [ 'TR', 'TH'] ) and ( CCCC in [ 'KWBC' ] ): 
            #    self.a1topic=self._USAA(AA) 
            if a1 == 'C6' :
                i=TT+AA[0]
                if self.debug: print( "AATopic 2.5 C6: " )
                if "ii" in self.tableC6[TT][AA[0]]:
                    iii = int(ii)
                    for iis in self.tableC6[TT][AA[0]]["ii"]:
                         (iilb, iiub) = iis.split("-") # get ii lower and upperbounds.
                         if (iii >= int(iilb) ) and ( iii <= int(iiub) ) :
                             self.a1topic=self.tableC6[TT][AA[0]]["ii"][iis]
                else:
                    if self.debug: print( "AATopic 3 self.a1topic=self.tableC6[%s][\"topic\"]" % i )
                    self.a1topic=self.tableC6[TT][AA[0]]

                if self.debug: print( "C6 self.a1topic=%s" % self.a1topic )
                
                if a2 == 'C3':
                    self.a2topic=self.tableC3[AA[1]]
                    if self.debug: print( "AATopic 4 self.a2topic=self.tableC3[%s]=%s" % (AA[1], self.a2topic) )
                else: #C4
                    if TT[0] in 'DGHJOPT':
                        self.a2topic=self.tableC4[AA[1]]
                    if self.debug: print( "AATopic 5 self.a2topic=self.tableC4[%s]=%s" % (AA[1], self.a2topic) )
            else: 
                if (a1 == 'C3'):
                    self.a1topic=self.tableC3[AA[0]]
                    if self.debug: print( "AATopic 6 self.a1topic=self.tableC3[%s] = \"%s\"" % (AA[0],self.a1topic) )

                    if ( a2 == 'C4' ):
                        if TT[0] in 'DGHJOPT':
                            self.a2topic=self.tableC4[ AA[1] ]
                        if self.debug: print( "AATopic 6.1 self.a2topic=self.tableC4[%s] = \"%s\"" % (AA[1],self.a2topic) )
                else:
                    if a1 == 'C1': idx='["topic"]'
                    else: idx='[0]'

                    
                    if self.debug: print( "AATopic 7 self.a1topic=self.table"+a1+"[%s]%s" % (AA,idx) )
                    exec( "self.a1topic=self.table"+a1+"[AA]"+idx )

                    if a2 == 'C1': idx='["topic"]'
                    else: idx='[0]'
                    exec( "self.a2topic=self.table"+a2+"[AA]"+idx )
                    if self.debug: print( "AATopic 8 self.a2topic=self.table"+a2+"[AA]%s = %s" % ( idx,self.a2topic ) )

            if self.a1topic  != "":
                if self.a2topic != "": 
                   topic = self.a1topic + "/" + self.a2topic
            elif hasattr(self,'a2topic') and self.a2topic != "":
                   topic = self.a2topic 
        return topic 

    """
        return the toppic hierarchy for a given AHL
    """

    def analyzeAHL(self,ahl):
        """
            given an instance and an AHL, return the topic tree that corresponds to it.

            Sample input:
               ahl=UGIN90_VOPB_181200_cd81eac262c21cffe4a83cd6572e6aba.txt

            Sample output:
               output: in/VOPB/air/wind/in/in

            if debug is set, in the constructor, it will be more verbose.

        """
        TT=ahl[0:2].upper()
        AA=ahl[2:4].upper()
        ii=ahl[4:6]
        T1=ahl[0].upper()
        T2=ahl[1].upper()
        CCCC = ahl[7:11]
        CCCCTopic=""
        country="unknown"
        gisc="unknown"
        if CCCC in self.tableCCCC:
            CCCCTopic=self.tableCCCC[ CCCC ]["centre"]
            country=self.tableCCCC[ CCCC ]["country_short"]
            if self.debug: print( "topic from CCCC %s -> %s (country: %s )" % ( CCCC, CCCCTopic, country ) )
        else: # last ditch go through CC in Table C1
            CC = CCCC[0:2]
            for c in self.tableC1:
                if "CC" in self.tableC1[c]:
                    if CC in self.tableC1[c]['CC']:
                        CCCCTopic=self.tableC1[c]['topic'] + GTStoWIS2.sep + CCCC
                        country=self.tableC1[c]['topic']
                        if self.debug: print( "topic from CCCC revised using Table C1: \"%s\" (country: %s)" % (CCCCTopic, country) )
                           
        ahlParseHint=self.tableA[ T1 ]

        if T1 == 'K':
           if debug: print( 'Applying CREX Table C7 ')
           i=TT+AA[0]
           if "ii" in self.tableC7[i]:
                iii = int(ii)
                for iis in self.tableC7[i]["ii"]:
                    (iilb, iiub) = iis.split("-") # get ii lower and upperbounds.
                    if (iii >= int(iilb) ) and ( iii <= int(iiub) ) :
                         self.a1topic=self.tableC7[i]["ii"][iis]
           else:
               self.a1topic=self.tableC7[i]
        elif TT == 'SZ':
           TTTopic="sea/"
        elif T1 == 'B': # Addressed messages, no idea...
           for g in self.tableGISC:
              if country in self.tableGISC[g]["responsible"]:
                 gisc=g
                 break
           return (gisc, country, CCCCTopic + "/addressed")
        else:
           ahlpiB=self.tableB[ TT ]
           if self.debug: print( "ahlpib: %s" % ahlpiB )
           TTTopic=ahlpiB[0]

        topic=TTTopic
        if self.debug: print( "topic from TT/B  \"%s\" -> \"%s\" " % ( TT, TTTopic ) )

        AATopic=self.__AATopic(TT,AA,ii,CCCC,ahlParseHint) 
        if AATopic :
           topic += GTStoWIS2.sep + AATopic

        # If CCCC found some other way, use AA to assign a country.
        if CCCCTopic == "":
           if AATopic in self.iso2countries:
               country=AATopic
               CCCCTopic = AATopic + GTStoWIS2.sep + CCCC
               if self.debug: print( "topic from CCCC revised to: \"%s\" " % CCCCTopic )

        if self.debug: print( "topic from AA/C: \"%s\" -> \"%s\"" % (AA, AATopic ) )

        

        iiTopic=self.__iiTopic(T1,T2,AA[1],ii,ahlParseHint)
        if iiTopic :
           topic += GTStoWIS2.sep + iiTopic

        if CCCCTopic:
           topic = CCCCTopic + GTStoWIS2.sep + topic

        if self.debug: print( "country to lookup for GISC: %s" % country )

        for g in self.tableGISC:
           if country in self.tableGISC[g]["responsible"]:
              gisc=g
              break
 
        if self.debug: 
            print( "topic from ii/C is: \"%s\" -> \"%s\" " % ( ii, iiTopic ) )
            print( "GISC: %s country: %s topic is: %s " % (gisc, country, topic) )
 
        return (gisc, country, topic)

    def mapAHLtoTopic(self,ahl):
        a = self.analyzeAHL(ahl)      
        return a[1] + GTStoWIS2.sep + a[2]
        
    def mapTopicToAHL(self,topic):
        print( "NotImplemented" )

    def mapAHLtoGISC(self,ahl):
        a=self.analyzeAHL(ahl)
        return a[0]
