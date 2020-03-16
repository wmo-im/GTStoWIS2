
Towards a Topic Hierarchy for the WIS
=====================================

In the March 2020 meeting, the WMO expert team on Computing and Telecommunications 
Systems has asked for a mapping to be created from the traditional WMO-386 AHL (
TTAAii CCCC ... abbreviated header lines) to a more readable topic hierarchy. 
This needs to be done in a standard way so that the AHL will end up under the 
same topic regardless of the nation doing the classification. 

So this sample provides a sample python script to interpret the tables 
as extracted from the WMO web site and expanded through testing with some
feeds. The topics chosen are taken from the existing tables, subject
to a few conventions, to create a starting point.

To do so, we need an executable version of the Tables from WMO 386. 
Those tables are in this directory with names like TableB.json
(where TableB includes both B1 and B2 in a single table). Where they
can be literally used, the tables are in json format. where some comments or
processing is required, the input is a comma separated value, or csv file.

There proved to many gaps in the existing tables.  Where the tables were
supplemented from other means, the description field included the keyword
**MISSING**, thus to find the changes made to the tables, one can execute::

   grep MISSING Table*

There is also an additional field in all the tables giving a topic to which
the table entry corresponds.  All hierarchies here are partial, indicating
only the portion derived from the AHL.

Testing
-------

On a Linux host with this directory present, execute the translation module, and
it will output the translation results for a number of sample AHL's::

   python GTStoWISTopic.py

   ahl=SACN37 CWAO 090807
   topic from CCCC is: ca/montreal_canadian_met_centre_que 
   ahlpib: ['observation/land', '', 'Aviation routine reports', 'FM 15 (METAR)\n']
   topic from TT/B is: observation/land 
   AATopic input: TT=SA, AA=CN, ahlHint={'Description': 'Surface data', 'T2': 'B', 'AA': 'C1', 'ii': '**', 'priority': '2/4'}
   self._AATopic=self.tableC1["CN"][0]
   topic from AA/C is: ca 
   topic from ii/C is:  
   topic is: ca/montreal_canadian_met_centre_que/observation/land/ca 
   ahl=SACN37 CWAO 090807, topic=ca/montreal_canadian_met_centre_que/observation/land/ca

This provides a means of inspection and consideration of the hierarchy.
one can add lines to the end of the file to put in more tests.



Conventions
-----------

in WMO 386, there are three concepts expressed in T1T2.

 * origin: who produce or is responsible for the data?
 * subject: what is the data partaining to?  (Surface, upper air, etc...)
 * audience: who is it for ( public, marine, aviation, etc...)
 * encoding: how is it encoded ( TAC, TDCF, etc...)
 * time:  when... (routine, interim synoptic, synoptic, speci)

Aside from names, topics are intended to be single words, and as generic as possible.

*upper-air* replaced by *air/upper*  .

Singular is used throughout, because otherwise everything would be plural,
and it leads to many occurrences of the word 's', with out any concomitant clarification.

Product pertinence: aloft,clouds,aviation,land,water,ocean,marine
*surface* is an odd choice for observations, since it leads to confusion with water/lake/ocean
where use of the word surface is more common. *land*, *ground* ::

   surface(land) -> land/
   aviation -> air/navigation
   marine   -> sea/navigation
               water/navigation (inland)


sea is shorter than ocean... also a bit less specific.  better suited for sea/navigation.

Gridded and grib data represents NWP products, so it could all be grouped
under model ?  model/prediction  model/analysis

Nothing is plural.


Origin
------

Top two levels of hierarchy, replace the CCCC with the two-letter iso code, followed by a centre identifier.
These centre identifiers are just mildly transformed versions of the description from the CCCC table.

To build CCCC, started with (https://www.wmo.int/pages/prog/www/ois/Operational_Information/VolumeC1/CCCC_en.pdf)
Volume C1 Attachment I in pdf format. After much manual work, 
there is a mapping built in the CCCC Table lookup.
tested on real feeds, and noticed many missing CCCC's.

found another source: http://weather.rap.ucar.edu/surface/stations.txt
merged the two. There are still some that are not in either source,
use the AA to guess. trying to at least assign them all to countries.

To build the centre name, took the description offerred, following conversions:
 
* converted to lower case
* removed parentheses ( )
* removed slashes /
* replaced spaces with underscore

left in some accented characters where present. Should we limit to 7-bit?
in order to restrict to Englishish names? Protocols support eight bit, 
but it will get very difficult to use in practice for people who do not
speak all world languages if full utf-8 is used with native language names.


Audience
--------

hmm.. 
SA's:
   observations/surface ?
   observations/surface/aerodrome  ?
   observations/aviation/ ?

aviation, marine, ...

Encoding
--------

The encoding should be expressed, as is universally done
in other domains, using file type suffixes.

file types::

        .txt for TAC
        .bufr for BUFR
        .crex for CREX
        .grib for grib

So the goal is that if there is information of similar content,
it should be in the same topic in the hierarchy, with the
file type suffix taking care of the encoding.

The topic tree should not mention encoding or format.
For example, T1=D,G,H all become "model"



Hierarchy
~~~~~~~~~

A topic hierarchy is, well hierarchical. That is, each following level should
specify or constrain the topic at the higher levels.  example::

   Topic from CCCC is: ru/magadan
   Tahlpib: ['air/aircraft', '', 'Aircraft reports', 'FM 41 (CODAR)', ' ICAO (AIREP)\n']
   Ttopic from TT/B is: air/aircraft
   TAATopic input: TT=UA, AA=RA, ahlHint={'Description': 'Upper air data', 'T2': 'B', 'A1': 'C1', 'A2': 'C1', 'ii': '**', 'priority': '2'}
   Tself.a1topic=self.tableC1[RA][0]
   Tself.a2topic=self.tableC1[AA][0] = ru
   Ttopic from AA/C is: ru
   Ttopic from ii/C is: air/navigation/special
   Ttopic is: ru/magadan/air/aircraft/ru/air/navigation/special
   ru/magadan/air/aircraft/ru/air/navigation/special:
   total 4
   -rw-rw-r-- 1 peter peter 76 Mar 16 07:17 UARA61_RUMG_161116_445a58ea753d18b066cf872b90c517e2.txt

In this case, we see *air* showing up twice. The first time, it comes from the TT to say that the type
of data being reported is from an aircraft. The second time it comes from the AAii and is about ...
Well I'm not sure what it is about. Does this make sense?

Sphere
~~~~~~

The hierarchy is especially evident in the dropping of hemi from hemispherical descriptions::

  sphere/north/west/east

* sphere --> topics that follow divide the sphere.
* sphere/north -> Northern Hemisphere.
* sphere/north/west -> 0-180 deg. west in northern hemisphere. (NW quarter sphere)
* sphere/north/west/east -> Eastern half (0-90 deg. west) of the NW quarter sphere.

