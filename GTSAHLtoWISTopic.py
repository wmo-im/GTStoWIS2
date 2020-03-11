#!/usr/bin/python3

"""
  module to map WMO 386 defined Abbreviated Header Lines to WIS topics.
  this module is installed with default table versions, which
  can be used directly, or overridden with TableDir argument to the constructor.

  usage:


"""
import json

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
                    exec( "print('\tTable" + tid + "[ %s ]= %s' % (j,self.table" + tid +"[j]))" )

    def readTables(self):

        # TableA
        self.tableA={}
        self.tableC1={}
        with open( self.tableDir + '/TableA.json', 'r' ) as m:
          self.tableA=json.load(m)
        with open( self.tableDir + '/TableC1.json', 'r' ) as m:
          self.tableC1=json.load(m)

        print( "Table A: %s" % json.dumps(self.tableA, indent=2) )
        print( "Table C1: %s" % json.dumps(self.tableC1, indent=2) )
        # TableB
        for t in [ 'B', 'C4', 'D2' ]:
            self.parseCSVB(t)

        for t in [ 'C2', 'C3', 'C5', 'C6', 'D1', 'D3' ]:
            self.parseCSV(t)


    def __init__(self,tableDir=None):
          
        self.tableDir = tableDir
        self.readTables()
        
    def iiTopic(self,t1,a2,ii,ahlHint):

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
                return "aloft/alerts/area" 
           return "aloft"
        elif t1 == 'U' and t2 == 'A':
           if inum < 60 :
                return "aloft/routine" 
           elif inum < 70:
                return "aloft/special" 
           elif inum < 80:
                return "aloft/special/ash" 
           else:
                return "aloft/reserved" 

        if 'D' in ahlHint['ii']:
            if ahlHint['ii'] == 'D2':
               k=a2+ii
               if k in self.tableD2:
                  return(self.tableD2[k])
               else:
                  return "ERROR undefined height" 
        return "" 
           


    def AATopic(self,AA,ahlHint):
        topic=""
        print( "AATopic input: AA=%s, ahlHint=%s" % ( AA, ahlHint) )
        if "AA" in ahlHint:
            atab = ahlHint["AA"]
            print( "atab is %s" % atab )
            if type(atab) is str:
                print( "self.AATopic=self.table"+atab+"[\""+AA+"\"]" )
                exec( "self.AATopic=self.table"+atab+"[\""+AA+"\"][0]" )
                print( "AATopic 1: set to %s" % self.AATopic )
                topic=self.AATopic
            else:
                return self.AATopic(AA,ahlHint["AA"])
        elif "A1" in ahlHint:
            a1 = ahlHint["A1"]
            exec( "self.a1topic=self.table"+a1+"[AA]" )
            
            a2 = ahlHint["A2"]
            exec( "self.a2topic=self.table"+a2+"[AA]" )

            if topic  != "":
                if self.a2topic != "": 
                   topic = self.a1topic + "/" + self.a2topic
            elif a2topic != "":
                   topic = self.a2topic 

        print(" AATopic returning: %s" % topic )
        return topic 

    """
        return the toppic hierarchy for a given AHL
    """

    def mapAHLtoTopic(self,ahl):
        TT=ahl[0:2].upper()
        AA=ahl[2:4].upper()
        ii=ahl[4:6]
        T1=ahl[0].upper()
        ahlParseHint=self.tableA[ T1 ]
        print( "ahlParseHint: %s" % ahlParseHint )

        if T1 == 'K':
           print( 'CREX Table C7 not yet implemented')
           TTTopic='crex'
        elif TT == 'SZ':
           print( 'TT=SZ not implemented yet.' )
        else:
           ahlpiB=self.tableB[ TT ]
           TTTopic=ahlpiB[0]

        topic=TTTopic

        AATopic=self.AATopic(AA,ahlParseHint) 
        if AATopic :
           topic += '/' + AATopic

        iiTopic=self.iiTopic(T1,AA[1],ii,ahlParseHint)
        if iiTopic :
           topic += '/' + iiTopic

        print( "ahlpib: %s" % ahlpiB )
        print( "topic from TT/B is: %s " % TTTopic )
        print( "topic from AA/C is: %s " % AATopic )
        print( "topic from ii/C is: %s " % iiTopic )
        print( "topic is: %s " % topic )
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
  t = topic_builder.mapAHLtoTopic(ahl)
