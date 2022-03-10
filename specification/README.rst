Introduction
~~~~~~~~~~~~

This chapter specifies the use of MQP for the WMO Information System 2.0

Use of Message Queueing Protocols for WMO
=========================================

Message Queueing Protocols (MQP) modernize how WMO Members exchange data. 
The traditional techniques involve sending messages over X.25 channels between
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

Message Queueing Protocols, such as AMQP and MQTT, for example, provide a
good base for the notification propagation that WMO still needs. There is a wide 
variety of MQP technologies, with no clear dominant one, and the emergence
of a better one in the future is not unlikely. The WMO's approach is to
to identify a few properties of MQP's that are core to the intended purpose, 
and not to bind too closely to an individual MQP.


Key Message Queueing Protocol Features
--------------------------------------

MQP will be used to route infomration through hubs (often called brokers)
that perform filtering based on hierarchical topics. MQTT is likely the
simplest embodiment of that plan, where it's core concepts embody precisely that
model.  AMQP, on the other hand, provides a swiss-army knife approach to messaging,
and one must prune features to only use a small subset. In AMQP only topic-based 
exchanges are used.

Supported Message Queueing Protocol 
--------------------------------------

WIS 2 will use MQTTv311 and MQTTv5



Message Format
=========================================

The message format makes the WMO implementation independent of a particular MQP.

The payload of messages, regardless of the MQP chosen, is JSON. Server-side representation may vary, but the message should represent a file that can be downloaded from a server.

A complete example being:: 

   {  "pubTime" : "20190120T045018.314854383", 
      "baseUrl" : "https://localhost/data/20190120", 
      "integrity": {"method": "sha512", "value": "A2KNxvks...S8qfSCw=='},
      "relPath" : "WIS/CA/CMC/UpperAir/04/UANT01_CWAO_200445___15103.txt", 
      "size": 457,
      "content": { "encoding": "utf-8", "value": "encoded bytes from the file" },
      "retPath" : "4Pubsub/92c557ef-d28e-4713-91af-2e2e7be6f8ab" 
   }


*  The *pubTime* marks when the file was posted on the first broker in the network.
   This allows easy calculation of propagation delay across any number of nodes.
   The date format looks like a floating point number,  but is the conventional
   YYYYMMDDTHHMMSS (in UTC timezone) followed by a fraction of a second after the
   decimal place.

   This is chosen rather than any sort of epochal second count for readability
   and to avoid worrying about leap seconds. This format is essentially ISO8601
   basic notation. The standard recommends a *T* be placed between date and time,
   and there is no convention to use a decimal marker for seconds. The use of a
   decimal marker allows for different users to give different levels of
   precision (milliseconds, microseconds, etc...) without ambiguity.

   In ISO8601 when times do not include a timezone marker, it is assumed to be local.
   In the meteorological domain, UTC is more natural. Leaving the Z out seems reasonable.

   The date stamp is critical for subscribers to prevent message loss by knowing
   their lag (how far behind the publisher they are.)

*  The *baseUrl* marks the static starting point to build the complete download URL.
   It represents the root of the download tree on the remote web server.

   Specifying the baseUrl in each message provides a number of benefits:
  
   - Use of schema gives mechanism for multiple protocols. Initially, subscribers
     shall support at least:

     * https
     * sftp
     * http/ftp (supported for legacy sources, though deprecated, only to be used for very public data.)

     This minimum list in will be reviewed in future from time to time.

   - enables third party transfer, where the broker announcing data doesn't necessarily
     have it locally, it might just know of a remote location, and not be interested in
     it for itself, but it could tell clients where to get it if they want it.

     Reduces load on broker, by having other nodes do the actual transfers.

   - allows many sources of data to be mixed in the same download stream.

   The baseUrl field can be replaced or turned into a list of alternatives 
   when re-publishing downloaded data.


*  the *relPath* is the rest of the download url.
   The public, portable name of the resources being published.
   Stays the same with republishing. Catenating the baseUrl and relPath normally
   results in a complete path to retrieve the upstream resource.
   The hierarchy in the relpath should match the topic hiearchy used to implement
   server-side filtering.

   The last element of the RelPath is the filename, and it should include an appropriate
   file type suffix. (examples: .txt, .bufr, .crex, .grib)


*  The *integrity* field specifies a checksum to be applied to the data to
   ensure that the download is accurate. A specific set of methods for calculating
   the checksum algorithms will be prescribed:

   - "sha512" -- the Secure Hash Algorithm 512 bits, value is base64 encoded.
   - "arbitrary" -- an arbitrary string is used to identify the value. 
   - "md5"   -- the Message Digest 5 hash (obsolete, perhaps will be rejected.)

*  The *Size* header contains an integer number of bytes contained in the file.
   together with the integrity, it provides additional assurance that file content
   was accurately received.


Optional Headers
--------------------------------------

By exchanging messages using only the above fields, enough metadata is provided
to permit downloads from peers with reasonable assurance.  Optional fields can 
additionally be included::

*  The *content* field can be used to embed small products within the message
   itself. Content will have an *encoding* field, of which two values are permitted:

   - *utf-8*
   - *base64*

   and the value will contain the body of the file in the appropriate encoding.

* The *retPath* header provides an alternate download URL, providing, for example,
  for direct retrieval from object stores.  This provides an optimization. 

* the *partitionStrategy* field can be included:: 

      { "method" : "partitioned",  -- either "partitioned" or "inplace"
        "blockNumber" : 0,         -- 1st partition/block sent. 
        "blockCount"  : 5,         -- how many blocks in total? 
        "blockSize"   : 52428800,  -- size of each block (except last one)
        "lastBlock"   : 125280     -- size of the last block.
      } 

  This field is used to transmit arbitrarily large files in pieces,
  to permit part of the file to be sent using multiple streams, and to
  reduce the amount of storage intervening systems need in order
  to transmit files. 
  
  When transmitting *inplace*, it means that the file is in one piece at source.
  for a *partitioned* file, only the referenced block is present at source.

  
Other Fields
--------------------------------------

It is expected that, similarly to what is done in SMTP (Postel's law - "Be liberal 
in what you accept, and conservative in what you send." ), headers not defined in
the payload format, are passed through without modification. The Canadian stack, for example
other headers: *blocks*, *mtime*, *atime*, "mode", "rename", "link", are used for purposes not
standardized by the WMO. Also, in the Canadian context, it can be used to signify 
file removal, in which case an *integrity* checksum cannot be provided.

The actual checksum of the data downloaded must be compared with the
advertised one to identify issues. One should always publish with the checksum
that matches what was downloaded, rather than what was advertised, to avoid loops.



Sample Implementations
--------------------------------------

The following implementations can be used to validate interoperability with
the standards:

- Canadian Sarracenia stack ( http://github.com/MetPX/sarracenia ) a complete reference implementation in Python >= 3.4. It runs on Linux, Mac, and Windows.

- proprietary interop? Jan?

- DWD?

- Japan? (how are DWD and Japan exchanging currently?)

- sarrac ( https://github.com/MetPX/sarrac ) is a partial C implementation. It is Linux only. There is also a libcshim to be able to tranparently implement data insertion with this tool, and libsarra allows C programs to post directly. There is consumer code as well (to read queues) but no downloading so far. This subset is meant to be used where python3 environments are impractical (some HPC environments).

Implementations by clients of the Canadian datamart service:

- node-sarra ( https://github.com/darkskyapp/node-sarra ) An embryonic implementation for node.js.

- ecpush ( https://github.com/TheTannerRyan/ecpush ) an simple client in Go ( http://golang.org )



Topic Hierarchy 
=========================================

A mapping from the traditional WMO-386 AHL (TTAAii CCCC ... AHL = abbreviated header lines) to a more readable topic hierarchy allows to represent GTS messages in WIS 2. 
This is done in a standard way so that the AHL will end up under the 
same topic regardless of the nation doing the classification. 

This sample provides a python script to interpret the tables 
as extracted from the WMO web site and expanded through testing with some
feeds. The topics chosen are taken from the existing tables, subject
to a few conventions, to create a starting point.

To do so, we need an executable version of the Tables from *WMO 386 Volume 1
Attachment II-5*.  Those tables are in this directory with names like TableB.json
(where TableB includes both B1 and B2 in a single table). Where they
can be literally used, the tables are in json format. where some comments or
processing is required, the input is a comma separated value, or csv file.

