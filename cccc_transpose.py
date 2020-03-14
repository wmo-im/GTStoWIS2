
"""
take the pdf version of the CCCC table, convert to txt via pdftotxt
This gives an output that is in three columns, one column at a time, per page.

In addition, in some cases, the middle column is two lines. The two
lines were merged by a manual pass.

This script transposes the three columns into a csv file, with four fields:

CCCC, CCCC_replacement, description, country

The CCCC value is printed twice to provide the placeholder column CCCC_replacement,
which will gradually be replaced. 




"""
debug=False

with open("CCCC_en.txt", 'r') as ccccfile:
  column=0
  table_index=0
  cccc = {}
  desc = {}
  country = {}
  in_a_page=True
  for l in ccccfile.readlines():
      if debug: print('l=%s, column=%d' % (l,column) )
      if 'Country' in l:
         if debug: print('found Country')
         in_a_page=True
         column=0 
         table_index=0
         cccc = {}
         desc = {}
         country = {}
         blanks = {}

      if in_a_page and len(l) > 3 :
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
             pass
      else:
         if debug: print('blank line, next column')
         if in_a_page:
             if column < 3:
                 if debug: print('blank line, next column %d ' % column)
                 column += 1
                 row_count=table_index
                 table_index=0
             else:
                 if debug: print('end of page')
                 column = 0
                 for i in range(0,row_count):
                     try:
                         print( "%d,%s,%s,%s,%s" % (i, cccc[i], cccc[i], desc[i], country[i] ) )
                     except Exception as ex:
                         print( "index issue: %s" % ex ) 
            
