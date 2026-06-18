# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzread.c

Purpose: Implements the high-level stdio read API for bzip2 streams.

Key points:
- `BZ2_bzReadOpen` validates parameters, allocates a `bzFile`, copies caller-provided unused bytes, initializes `BZ2_bzDecompressInit`, and primes `strm.next_in/avail_in`.
- `BZ2_bzRead` fills the input buffer from `FILE*`, calls `BZ2_bzDecompress`, handles `BZ_STREAM_END`, zero-length reads, I/O errors, and unexpected EOF.
- `BZ2_bzReadClose` ends the decompressor if initialized and frees the wrapper.
- `BZ2_bzReadGetUnused` returns unread bytes only after stream end.

Dependencies and interactions:
- Calls core decompressor entry points declared in `bzlib.h`.
- Uses `bz_feof` from `bzstdio.c`.
- Uses `BZ_SETERR` and `bzFile` from `bzlib_stdio_private.h`.

Research notes:
- Read-side behavior is streaming and incremental. It can return partial output at stream end and exposes unused compressed bytes for concatenated or framed consumers.
- The function treats reads from a write-mode `bzFile` as sequence errors.
