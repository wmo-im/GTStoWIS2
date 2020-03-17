"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2("GTStoWIS2",debug=True,dump_tables=False)



ahl="SACN37 CWAO 090807"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SSAS33 KWBC 14220"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SNFI01 KWBC 142200"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="IUPA54_LFPW_150000"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="IUPD48_SOWR_150004"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )


ahl="FTPA32_KWBC_151015_AAA"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SRFL20_KWAL_151016"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SXWY50_KWAL_151017"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SNVB21_AMMC_151000"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SROK30_KWAL_151111"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SXNE55_KWAL_151116"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="UANT01_CWAO_15111"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="NXUS60_PHFO_151120"  # PHFO not in WMO CCCC Table... Honolulu forecast office.
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SRWV30_KWAL_151120_"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="FTZZ40_KAWN_151121"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SZMS01_WMKK_151123"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="UBUS31_KWBC_151125"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="TRCA01_KWBC_151000"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="THCA01_KWBC_151100"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="IUSV51_KWBC_151150"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="IUSV52_KWBC_151150"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SRUS54_KOHX_151216"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="CXUS43_KBIS_151217"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="NZUS93_KARX_151217"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="YVXX84_KAWN_151200"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="SFTX57_KWAL_151220"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="BMBB91_KJAX_151224"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="IUSZ52_KWBC_151235"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="INGX27_KNES_151252"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="UBFL90_KWBC_151310"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="USBZ05_SBBR_151200"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="HEPF98_KWBC_151800"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

ahl="HGJF98_KWBC_151800"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

# example of CCCC not in any table.
ahl="SIIN90_VIHS_160300"
print( "ahl=%s" % ( ahl ) )
t = topic_builder.mapAHLtoTopic(ahl)
print( "topic=%s\n" % ( t ) )

