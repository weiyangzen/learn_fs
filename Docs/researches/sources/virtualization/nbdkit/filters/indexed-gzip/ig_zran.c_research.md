# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.c

Adapts Mark Adler’s zran random-access deflate indexing to nbdkit `next->pread()` I/O. `ig_deflate_index_build()` scans the compressed stream once, detects RAW/ZLIB/GZIP mode, inflates with `Z_BLOCK`, and records access points about every configured span bytes of uncompressed output.

The build path stores access points with `add_point()`, records the final mode and uncompressed length, and assigns the completed index into the filter handle. It returns standard zlib negative errors or `Z_NBDKIT_ERROR` when an nbdkit callback set an error.

`ig_deflate_index_extract()` finds the nearest access point by binary search, resets the reusable inflate stream, primes bit alignment when needed, sets the saved dictionary, skips to the requested uncompressed offset, then inflates into the caller buffer. It has explicit logic for continuing across gzip members.

The implementation relies on `h->compressed_size` to bound upstream reads. Because extraction mutates `index->strm`, the filter wraps calls with a mutex.
