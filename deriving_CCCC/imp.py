
"""
0         1         2         3         4         5         6         7         8
01234567890123456789012345678901234567890123456789012345678901234567890123456789012
ON MONTREAL RIV HAR CWGJ               47 14N  084 35W  559      X             8 CA

download stations.txt from:   http://weather.rap.ucar.edu/surface/stations.txt
Then convert to same format using this script redirecting output to stations.json

"""
with open("stations.txt") as sf:
   for l in sf.readlines():
       if l[0] == '!':
          continue

       if l[0] != ' ':
          country_description=l
          continue

       CCCC=l[20:24]
       if CCCC == "    ":
          continue

       country=l[81:83].lower()
       description=l[3:15].replace('/','_').replace('(','').replace(')','').strip()
       description=description.strip()
       if country == 'us':
           description +=' '+l[0:2]
           
       lat= int(l[39:41]) + int(l[42:44])/60.0
       if l[44] == 'S': lat = -lat

       lon= int(l[47:50]) + int(l[51:53])/60.0
       if l[53] == 'W': lon = -lon

       elev= int(l[55:60])

       desc=description.lower().replace(' ','_')
       print( '"%s": { "centre":"%s", "geometry": { "type":"Point", "coordinates": [ %g, %g, %g  ] }, "description":"MISSING (from stations.txt) %s", "Country":"%s" }},' % ( CCCC, desc, lon, lat, elev, description, country ) )
