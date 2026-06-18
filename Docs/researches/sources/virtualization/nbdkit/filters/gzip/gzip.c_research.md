# File Research: sources/virtualization/nbdkit/filters/gzip/gzip.c

Implements a readonly gzip decompression filter by eagerly inflating the entire upstream export into an anonymous temporary file. A global mutex ensures only the first `gzip_prepare()` performs decompression.

`gzip_open()` always opens the underlying plugin readonly. `do_uncompress()` reads the compressed export in 4 MiB chunks, uses `inflateInit2(16 + MAX_WBITS)` for gzip streams, writes decompressed output to a `mkostemp()`/`mkstemp()` temporary file, and records compressed and uncompressed sizes.

The filter reports readonly, no extents, cache emulation, and multi-conn consistency because reads come from the stable temp file. `gzip_get_size()` verifies the compressed upstream size did not change before returning the cached uncompressed size.

`gzip_pread()` loops over POSIX `pread()` against the temp file and rejects unexpected EOF. The temp fd is closed at unload.
