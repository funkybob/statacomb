=========
statacomb
=========

Simple statistics/metrics gathering and display tool

----------
The layout
----------


1. A stats sink server.

   This server listens on a UDP port, and receives JSON blobs.

   The blobs are of the format {'source': sourcename, 'values': {data}}

   It will insert these values, along with a timestamp and the source IP, into a Postgres database.

2. Many stats sources.

   Client apps can lob metrics bundles at the sink server to record.  Being UDP it's not going to cause a slow-down.

3. A web interface.

   Some aggregaion and filtering to allow you to chart your metrics over time.


-----------
Quick Start
-----------

1. Create a DB

   .. code-block:: sh

      createdb stats
      psql stats

   .. code-block:: sql

      CREATE TABLE records (
          id SERIAL,
          ts TIMESTAMP,
          source TEXT,
          src_ip INET,
          values JSON
      );

2. Start the sink server

   .. code-block:: sh

      python -m statacomb.server --dbname stat

3. Start the web server

   This requires gunicorn to be installed.

   .. code-block:: sh

      python -m statacomb.web --dbname stat

4. Send in some data

   .. code-block:: python

      >>> from statacomb.client import SinkHost
      >>> import random
      >>> import time
      >>> h = SinkHost(source='sample')
      >>> for x in range(100):
      >>>    h.send_data({'total': random.randint(0, 100)})
      >>>    time.sleep(5)

5. View the results in your browser at http://localhost:8000/

