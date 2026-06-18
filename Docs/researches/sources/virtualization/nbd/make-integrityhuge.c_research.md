# File Research: sources/virtualization/nbd/make-integrityhuge.c

Utility for generating a synthetic transaction stream to test oversized/randomized NBD operations.

It writes request/reply packet pairs to stdout for 250 transactions over a 50 MB virtual file. It randomly chooses aligned offsets and lengths, emits reads or writes, sometimes forces FUA writes, sometimes emits flushes, and finally writes a disconnect request.

It uses NBD request/reply structures and byte-order helpers from shared headers. The output is intended as binary test data, not human-readable logging.
