"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2(debug=False,dump_tables=True)

with open( 'AHL_examples.txt', 'r' ) as headers:
    hh=headers.readlines()

print( "Tests, count: %d" % len(hh) )
n=1
for hl in hh:
    ahl= hl.split(',')[0]
    print( "%3d - %s" % ( n, ahl ) )
    t = topic_builder.mapAHLtoTopic(ahl)
    print( "\ttopic=%s GISC=%s\n" % ( t, topic_builder.mapAHLtoGISC(ahl) ) )
    n+=1

