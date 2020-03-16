
"""
Take the pdf version of the CCCC table, convert to txt via pdftotxt
This gives an output that is in three columns, one column at a time, per page.

In addition, in some cases, the middle column is two lines. The two
lines were merged by a manual pass.

This script transposes the three columns into a csv file, with four fields:

CCCC, CCCC_replacement, description, country

The CCCC value is printed twice to provide the placeholder column CCCC_replacement,
which will gradually be replaced. 


WARNING: 
   A great deal of manual edits were done to produce the initial json file.
   This is only useful for historical purposes, documenting the method of work.

"""
debug=False

import json

with open("TableC1.json", 'r') as tc1:
    TableC1 = json.load(tc1)

def map_centre_from_desc( cccc, iso2country, desc ):

    l=desc.lower().replace('/','_').replace('.',' ').replace('(','').replace(')','').replace(',','').replace("'","").replace('"',"").split()
    if (l[0] == "call") or ( l[0] == '--'):
       return iso2country + "/" + cccc
    return iso2country + "/" + '_'.join(l)
   


def map_country( cccc, cd ):

   if cd.startswith('--') or cd.startswith("WMO"):
      return "unmatched"

   for wmo2 in TableC1:
       if cd == TableC1[wmo2][1]:
          return TableC1[wmo2][0]

   if debug : print( 'mapping: %s' % cd )

   if "Antarctic" in cd : return "aq"
   elif "Canada" in cd : return "ca"
   elif "Indian Ocean" in cd : return "io"
   elif "Europe" in cd or "EUMETSAT" in cd: return "europe"
   elif "French Polynesia" in cd: return "pf"
   elif "Faroe" in cd: return "dk"
   elif "Gough" in cd: return "sh"
   elif "Mariana" in cd : return "mp"
   elif "Nauru" in cd : return "nr"
   elif "Nigeria" in cd : return "ng"
   elif "Réunion" in cd : return "re"
   elif "Russia" in cd : return "ru"
   elif "Helena" in cd : return "sh"
   elif "U.S.A" in cd or "United States of America" in cd : return "us"

   print( "no match found for: %s" % cd )     
   return( "unmatched" )

with open("CCCC_en.txt", 'r') as ccccfile:
  column=0
  table_index=0
  cccc = {}
  desc = {}
  country = {}
  in_a_page=True
  for l in ccccfile.readlines():
      if debug: print('row=%s, column=%d, len(l)=%d, l=%s' % (table_index, column, len(l), l) )
      if 'Country Name' in l:
         if debug: print('found Country')
         in_a_page=True
         column=0 
         table_index=0
         cccc = {}
         desc = {}
         country = {}

      elif len(l) > 1:
          if in_a_page: 
             if column==1:
                 if debug: print('assigning CCCC: %s' % l.strip() )
                 cccc[table_index]=l.strip()    
                 table_index += 1
             elif column==2:
                 if debug: print('assigning desc: %s' % l.strip() )
                 desc[table_index]=l.strip()    
                 table_index += 1
             elif column==3:
                 if debug: print('assigning country: %s' % l.strip() )
                 country[table_index]=l.strip()    
                 table_index += 1
      else:
         if debug: print('blank line, next column in_a_page=%s' % in_a_page )
         if in_a_page:
             if column < 3:
                 column += 1
                 if debug: print('blank line, column is now %d ' % column)
                 row_count=table_index
                 table_index=0
             else:
                 if debug: print('end of page len(cccc)=%d, len(country)=%d, len(desc)=%d' % ( len(cccc), len(country), len(desc) ))
                 column = 0
                 for i in range(0,len(cccc)):
                     #if i >= len(cccc):
                     #    print( "huh? i=%d > len(cccc)=%d" % ( i, len(cccc) ) ) 
                     #    continue
                     #if i >= len(country):
                     #    print( "huh? i=%d > len(country)=%d" % ( i, len(country) ) ) 
                     #    continue
                     iso2country=map_country(cccc[i],country[i])
                     wis_centre = map_centre_from_desc( cccc[i], iso2country, desc[i] )
                     print( '"%s": { "centre":"%s", "description":"%s","country":"%s" },' % (cccc[i], wis_centre, desc[i], country[i] ) )
