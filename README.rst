
Towards a Topic Hierarchy for the WIS
=====================================

In the March 2020 meeting, the WMO expert team on Computing and Telecommunications 
Systems asked for a mapping to be created from the traditional WMO-386 AHL (
TTAAii CCCC ... AHL = abbreviated header lines) to a more readable topic hierarchy. 
This needs to be done in a standard way so that the AHL will end up under the 
same topic regardless of the nation doing the classification. 

This sample provides a python script to interpret the tables 
as extracted from the WMO web site and expanded through testing with some
feeds. The topics chosen are taken from the existing tables, subject
to a few conventions, to create a starting point.

To do so, we need an executable version of the Tables from WMO 386. 
Those tables are in this directory with names like TableB.json
(where TableB includes both B1 and B2 in a single table). Where they
can be literally used, the tables are in json format. where some comments or
processing is required, the input is a comma separated value, or csv file.

STATUS
------

There proved to many gaps in the existing tables. Where the tables were
supplemented from other means, the description field included the keyword
**MISSING**, thus to find the changes made to the tables, one can execute::

   grep MISSING Table*

There is also an additional field in all the tables giving a topic to which
the table entry corresponds. All hierarchies here are partial, indicating
only the portion derived from the AHL. 

Initial attempts were made to complete TableCCCC, but it proved fruitless,
so added a field to C1 to associate the first to letters of the origin,
aka: C1, C2,  to the corresponding country. This allows generally correct
attribution of an origin to a country.

The data set used for validation had perhaps data the americans consider
domestic which has a number of products not defined un the WMO tables.
Clarification of additional table entries would be helpful.


Testing
-------

On a Linux host with this directory present, execute the translation module, and
it will output the translation results for a number of sample AHL's::

   git clone https://github.com/wmo-im/GTStoWIS2
   cd GTStoWIS2
   python test.py


   UGIN90_VOPB_181200_cd81eac262c21cffe4a83cd6572e6aba.txt

   topic from CCCC VOPB -> in/VOPB 
   ahlpib: ['air/wind', '', 'Upper wind (Part B)', 'FM 32 (PILOT)/FM 33(PILOT SHIP)/FM 34(PILOT MOBIL)\n']
   topic from TT/B  "UG" -> "air/wind" 
   AATopic 1 input: TT=UG, AA=IN, ahlHint={'Description': 'Upper air data', 'T2': 'B', 'A1': 'C1', 'A2': 'C1', 'ii': '**', 'priority': '2'}
   AATopic 7 self.a1topic=self.tableC1[IN]["topic"]
   AATopic 8 self.a2topic=self.tableC1[AA]["topic"] = in
   topic from AA/C: "IN" -> "in/in"
   topic from ii/C is: "90" -> "" 
   topic is: in/VOPB/air/wind/in/in 
   topic=in/VOPB/air/wind/in/in

This provides a means of inspection and consideration of the hierarchy.
one can add lines to the end of the file (*AHL_examples.txt*) to put in more tests. 




Conventions
-----------

in WMO 386, there are five concepts expressed in the AHL:

 * origin: who produce or is responsible for the data?
 * subject: what is the data partaining to?  (Surface, upper air, etc...)
 * audience: who is it for ( public, marine, aviation, etc...)
 * encoding: how is it encoded ( TAC, TDCF, etc...)
 * time:  when... (routine, interim synoptic, synoptic, speci)

Note that the '/' is used as a topic separator here, as is used in MQTT.
One will need to replace '/' with '.' in AMQP deployments, which is one
reason why neither character can be permitted in any placename or
topic label.

Also using English as a single, most accessible language to write the topics
in. Translation tables could be created,  but a single language needs to be
used for international data exchange to be coherent.

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

Subject
-------

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

