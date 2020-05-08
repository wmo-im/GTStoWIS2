"""
 merge the table from TableCCC and stations.json (created by imp.py)
"""
import json
import sys

cf=open("TableCCCC.json","r")
origins=json.load(cf)
cf.close()

print ( "CCCC read" )

sf=open("stations.json","r")
stations=json.load(sf)
sf.close()

print ( "Stations read" )

sys.exit(0)

all=list(set().union(stations.keys(),origins.keys()))
all.sort()

for c in all:
     m='hoho'   
     if c in origins.keys():
         print('c is in origin.keys: %s' % origins[c] )
         if c in stations.keys():
            i=origins[c].update(stations[c])
            m="both"
         else:
            i=origins[c]
            m="CCCC"
     else:
         print('c is in stations.keys: %s' % stations[c] )
         i=stations[c]
         m="stations"

     j=json.dumps(i,ensure_ascii=False,separators=(', ',':'))
     #print( '"%s":%s, %s' % (c, j, m) )
