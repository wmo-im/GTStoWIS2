"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2("GTStoWIS2",debug=True,dump_tables=True)

with open( 'AHL_examples.txt', 'r' ) as headers:
    hh=headers.readlines()

print( "Tests, count: %d" % len(hh) )
n=1
for hl in hh:
    ahl= hl.split(',')[0]
    print( "%3d - %s" % ( n, ahl ) )
    t = topic_builder.mapAHLtoTopic(ahl)
    print( "topic=%s\n" % ( t ) )
    n+=1

