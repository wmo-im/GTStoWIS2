"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2(debug=False,dump_tables=False)

with open( 'AHL_examples.txt', 'r' ) as headers:
    hh=headers.readlines()

print( "Tests, count: %d" % len(hh) )
n=1
for hl in hh:
    ahl= hl.strip().split(',')[0]
    t = topic_builder.mapAHLtoTopic(ahl).replace('/','.')
    p = topic_builder.mapAHLtoRelPath(ahl)
    print( "summary: %3d - %s mapped to:\n AMQP sub-topic: %s\n\trelPath: %s\n\n" % \
        ( n, ahl, t, p ) )
    n+=1

