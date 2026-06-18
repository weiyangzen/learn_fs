# File Research: sources/virtualization/nbdkit/filters/lzip/lzipfile.h

Declares the opaque `lzipfile` abstraction used by `lzip.c`. Exposes open/close, total uncompressed size, maximum uncompressed block size, and block read APIs.

`lzipfile_read_block()` returns a newly allocated decompressed member containing the requested offset and reports that block’s uncompressed start and size. The caller owns the returned data.

This header hides liblzma and archive-member parsing details from the nbdkit filter glue.
