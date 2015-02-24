# statacomb
Simple statistics/metrics gathering and display tool

# The layout


1. A stats sink server.

This server listens on a UDP port, and receives JSON blobs.

The blobs are of the format {'source': sourcename, 'values': {data}}

It will insert these values, along with a timestamp and the source IP, into a Postgres database.

2. Many stats sources.

Client apps can lob metrics bundles at the sink server to record.  Being UDP it's not going to cause a slow-down.

3. A web interface.

Some aggregaion and filtering to allow you to chart your metrics over time.
