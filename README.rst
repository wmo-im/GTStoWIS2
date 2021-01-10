
Use of Message Queueing Protocols for WMO
=========================================

The committee whose work is documented by this repository is tasked with modernizing
the method used by the members of the World Meteorological Organization to circulate
data. The traditional techniques involve sending messages over X.25 channels between
weather centres using methods defined by the WMO 306 (Manual on Codes) and WMO 386 
(Manual on the GTS.) All of those technologies pre-date the internet and are obsolete. 

There are now many technologies which can be adopted from the wider world, and
most of the problem solved by those specifications aren't a problem any more.
Sending data is something very common on the internet, protocols like TCP, or even
higher level, file transfers, such as SFTP or S3 exist and work well.

Weather forecasting, in particular, has a need for timely data dissemination.
A two day old forecast is an (poor) observation. If data arrives too late, it 
cannot be used to produce a forecast, or worse, a severe weather warning. 
So there is the long standing need "meteorological real-time" alerting, where 
the time to transmit data is on the order of a few seconds.

Message Queueing Protocols (MQP), such as AMQP and MQTT, for example, provide the 
basis for the notification propagation that WMO still needs. There is a wide 
variety of such technologies, with no clear dominant one, and the emergence
of a better one in the future is not unlikely. The WMO's approach to use
of the technologies is to identify a few properties of MQP's that are core
to the intended purpose, and not to bind too closely to an individual one.


Message Queueing Protocol Features
----------------------------------

The plan is to have messages routed through hubs (often called brokers)
that perform filtering based on hierarchical topics. MQTT is likely the
simplest embodiment of that plan, where it's core concepts embody precisely that
model.  AMQP, on the other hand, provides a swiss-army knife approach to messaging,
and one must prune features to only use a small subset. In AMQP only topic-based exchanges
are used.


Message Format
--------------

The message format was hashed out in WMO meetings in 2018 and 2019, and
the results have been imported into this repository.  There is no intent to 
lock the WMO into a particular MQP.  Rather the message encoding is MQP 
agnostic JSON format, as defined in the `message_format <message_format>`_ sub-directory
in this repository.

For more information on the message format please consult the README.rst
file in that directory.


Towards a Topic Hierarchy for the WIS
-------------------------------------

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

It is now in a state where we can ask for a wider review of the proposal.

<<<<<<< HEAD
USAGE
-----
=======
INSTALLATION
~~~~~~~~~~~~

The module is a python package. 
Installing::

   git clone https://github.com/wmo-om/GTStoWIS2.git
   cd GTStoWIS2
   pip3 install -e .

and then the package can be used from a python application.


USAGE
~~~~~

If you have some code that wants to insert traditional GTS data onto WIS,
if you are using python, you can do the following::

   import GTStoWIS2

   topic_mapper = GTStoWIS2.GTStoWIS2()

   for ahl in [ 'IUPA54_LFPW_150000', 'A_ISID01LZIB190300_C_EDZW_20200619030401_18422777' ]:
       topic = topic_mapper.mapAHLtoTopic( ahl )
       print( 'ahl: %s, mapped to: %s' % ( ahl, topic ) )

so then you could place the file in a corresponding sub-directory::

   import shutils

   os.mkdir( topic ) 
   shutils.move( fn, topic + os.sep + fn )

and then create announcements to advertise the file.


STATUS
~~~~~~

There proved to many gaps in the existing tables. Where the tables were
supplemented from other means, the description field included the keyword
**MISSING**, thus to find the changes made to the tables, one can execute::

   grep MISSING Table*

There is also an additional field in all the tables giving a topic to which
the table entry corresponds. All hierarchies here are partial, indicating
only the portion derived from the AHL. 

Initial attempts were made to complete TableCCCC, but it proved fruitless,
as many countries have ORIGIN codes which are not in the WMO table.
Added a field to Table C1 to associate the first to letters of the origin,
aka: C1, C2,  to the corresponding country. This allows generally correct
attribution of an CCCC origin to a country.

The data set used for validation had data Americans likely consider
domestic, which has a number of products not defined un the WMO tables.
Clarification of additional table entries would be helpful.

Also Table D3 is so far handled in the python module itself, ignoring
the contents of the table.


Testing
~~~~~~~

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
below were the initial ideas:

*upper-air* replaced by *air/upper*  .

This change was reverted (so upper-air now appears in the topic hierarchy) following some feedback.  Further discussion welcome in ( https://github.com/wmo-im/GTStoWIS2/issues/2 )

Singular is used throughout, because otherwise everything would be plural,
and it leads to many occurrences of the word 's', with out any concomitant clarification.


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

   1 - UARA61_RUMG_161116_445a58ea753d18b066cf872b90c517e2.txt

   topic from CCCC RUMG -> magadan (country: ru )
   ahlpib: ['air/aircraft', '', 'Aircraft reports', 'FM 41 (CODAR)', ' ICAO (AIREP)\n']
   topic from TT/B  "UA" -> "air/aircraft"
   AATopic 1 input: TT=UA, AA=RA, ahlHint={'Description': 'Upper air data', 'T2': 'B', 'AA': 'C1', 'ii': '**', 'priority': '2'}
   AATopic 2 self._AATopic=self.tableC1["RA"]["topic"]
   topic from AA/C: "RA" -> "ru"
   country to lookup for GISC: ru
   topic from ii/C is: "61" -> "air/navigation/special"
   GISC: Moscow country: ru topic is: magadan/air/aircraft/ru/air/navigation/special
   GISC,country,topic=Moscow, ru, magadan/air/aircraft/ru/air/navigation/special

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

This spherical notation was an initial proposal, which from feedback, evolved to use
numerical lat/long ranges, e.g. 0-90m/0-90w ::

  5 - IUPA54_LFPW_150000

   topic from CCCC LFPW -> toulouse_centre_régional_de_télécommunications (country: fr )
   ahlpib: ['observation/air/upper', '', 'Upper air\n']
   topic from TT/B  "IU" -> "observation/air/upper"
   AATopic 1 input: TT=IU, AA=PA, ahlHint={'Description': 'Observational data (Binary coded) - BUFR', 'T2': 'B', 'A1': 'C6', 'A2': 'C3', 'ii': '**', 'priority': '2'}
   AATopic 2.5 C6:
   AATopic 3 self.a1topic=self.tableC6[IUP]["topic"]
   C6 self.a1topic=pilot-profiler
   AATopic 4 self.a2topic=self.tableC3[A]=0-90n/0-90w
   topic from AA/C: "PA" -> "pilot-profiler/0-90n/0-90w"
   country to lookup for GISC: fr
   topic from ii/C is: "54" -> ""
   GISC: Toulouse country: fr topic is: toulouse_centre_régional_de_télécommunications/observation/air/upper/pilot-profiler/0-90n/0-90w
   GISC,country,topic=Toulouse, fr, toulouse_centre_régional_de_télécommunications/observation/air/upper/pilot-profiler/0-90n/0-90w


Results
-------

It may help to see where GTS products will land in the topic hierarchy.  There is a file AHL_examples.txt in this 
repository, which is interpreted by the tables and code in the repository as follows::
    
  fractal% python test.py | grep '^summary:'  | sed 's/summary: ... - //g' | sed 's/mapped to:/-->/g'

  IUFH13_EUMG_290000_a3550000251d79506cf3bd9e624a7830.bufr --> eu/eumetsat_darmstadt/observation/air/upper/satellite/radiance/tropics/90e-0
  HHOG15_EGRR_290000_efeecc850c17e9650b16fe9e8eb5735d.grib --> gb/bracknell/model/height/somewhere/tableC3O/036h
  HHMG20_EGRR_290000_b1e617564322a7c7e6cacb2ee579828a.grib --> gb/bracknell/model/height/somewhere/tableC3M/036h
  HRYA92_EGRR_290000_393b2b09047f2cddb6b7ce6df6a768d7.grib --> gb/bracknell/model/humidity/relative/somewhere/tableC3Y/analysys
  .
  .
  . 

Shows WMO 386 AHL's and feeds them to the mapAHLtoTopic call in the GTStoWIS2 python module.
