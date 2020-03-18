"""

Place test AHL's here to see how they are interpreted.

"""

print ( "%s" % __file__ )

import GTStoWIS2

topic_builder=GTStoWIS2.GTStoWIS2("GTStoWIS2",debug=True,dump_tables=False)

headers = [ 
   "SACN37 CWAO 090807",
   "SSAS33 KWBC 14220",
   "SNFI01 KWBC 142200",
   "IUPA54_LFPW_150000",
   "IUPD48_SOWR_150004",
   "FTPA32_KWBC_151015_AAA",
   "SRFL20_KWAL_151016",
   "SXWY50_KWAL_151017",
   "SNVB21_AMMC_151000",
   "SROK30_KWAL_151111",
   "SXNE55_KWAL_151116",
   "UANT01_CWAO_15111",
   "NXUS60_PHFO_151120"  # PHFO not in WMO CCCC Table... Honolulu forecast office.
   "SRWV30_KWAL_151120_",
   "FTZZ40_KAWN_151121",
   "SZMS01_WMKK_151123",
   "UBUS31_KWBC_151125",
   "TRCA01_KWBC_151000",
   "THCA01_KWBC_151100",
   "IUSV51_KWBC_151150",
   "IUSV52_KWBC_151150",
   "SRUS54_KOHX_151216",
   "CXUS43_KBIS_151217",
   "NZUS93_KARX_151217",
   "YVXX84_KAWN_151200",
   "SFTX57_KWAL_151220",
   "BMBB91_KJAX_151224",
   "IUSZ52_KWBC_151235",
   "INGX27_KNES_151252",
   "UBFL90_KWBC_151310",
   "USBZ05_SBBR_151200",
   "HEPF98_KWBC_151800",
   "HGJF98_KWBC_151800", # example of CCCC not in any table.
   "SIIN90_VIHS_160300",
   "PEIK98_KWNH_180000",
   "PEBI88_KWNH_171800",
   "PSBC04_KWNH_180000",
   "ZCNM85_KWBE_180000"
]

for ahl in headers:
    print( "   %s" % ( ahl ) )
    t = topic_builder.mapAHLtoTopic(ahl)
    print( "topic=%s\n" % ( t ) )

