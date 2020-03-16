
"""
 
 merge the table from the 

"""
import json

cf=open("../TableCCCC.json","r")
origins=json.load(cf)
cf.close()

#print( " origins[%s]=%s" % ( 'CWAO', origins['CWAO'] ) )

sf=open("stations.json","r")
stations=json.load(sf)
sf.close()

#print( " stations[%s]=%s, present in origins?: %s" % \
#    ( 'CWGJ', stations['CWGJ'], 'CWCJ' in origins ) )

#print( " origins.keys() = %s " % origins.keys() )

all=list(set().union(stations.keys(),origins.keys()))
#print("len of all: %d" % len(all) )
all.sort()
#print("len of all: %d" % len(all) )

for c in all:
        
     if not c in origins.keys():
         i=stations[c]
     elif ( origins[c]['description'] == '--' ) and (c in stations.keys() ):
         i=stations[c]
     else:
         i=origins[c]

     j=json.dumps(i,ensure_ascii=False,separators=(', ',':'))
     print( '"%s":%s,' % (c, j) )
