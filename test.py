"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2(debug=True,dump_tables=True)

with open( 'AHL_examples.txt', 'r' ) as headers:
    hh=headers.readlines()

print( "Tests, count: %d" % len(hh) )
n=1
for hl in hh:
    ahl= hl.strip().split(',')[0]
    print( "input: %3d - %s" % ( n, ahl ) )
    t = topic_builder.analyzeAHL(ahl)
    print( "GISC,country,topic=%s" % ', '.join(t) )
    if t[1] +'/' != t[2][0:3]:
       tt = t[1] + '/' + t[2]
    else:
       tt = t[2]
    print( "summary: %3d - %s mapped to: %s\n\n" % ( n, ahl, tt ) )
    n+=1

