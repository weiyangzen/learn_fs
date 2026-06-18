# File Research: sources/virtualization/nbdkit/filters/lzip/lzipindex.h

Defines the lzip archive-member index structures and operations. `lzip_index_member` stores uncompressed data offset/size and compressed member offset/size.

`lzip_index` stores total uncompressed size, optional uniform block size for constant-time lookup, and a vector of members in reverse order. The comments explain that random access is effective for multi-member lzip files, especially those produced by tools such as `plzip` or `tarlz`.

Declares prepend, finalize, search, and destroy functions. The search API returns the member containing a given uncompressed offset or NULL.
