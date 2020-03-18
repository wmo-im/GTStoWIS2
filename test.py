"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2("GTStoWIS2",debug=True,dump_tables=False)

with open( 'AHL_examples.txt', 'r' ) as headers:
    for hl in headers:
        ahl= hl.split(',')[0]
        print( "   %s" % ( ahl ) )
        t = topic_builder.mapAHLtoTopic(ahl)
        print( "topic=%s\n" % ( t ) )

