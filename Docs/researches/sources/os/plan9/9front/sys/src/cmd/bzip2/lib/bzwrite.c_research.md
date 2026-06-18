# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzwrite.c

Purpose: Implements the high-level stdio write API for bzip2 streams.

Key points:
- `BZ2_bzWriteOpen` validates file, block size, verbosity, and work factor, allocates `bzFile`, defaults work factor 0 to 30, and initializes compression.
- `BZ2_bzWrite` feeds input to `BZ2_bzCompress` with `BZ_RUN`, writing produced bytes to the wrapped `FILE*`.
- `BZ2_bzWriteClose` delegates to `BZ2_bzWriteClose64`.
- `BZ2_bzWriteClose64` optionally finishes compression with `BZ_FINISH`, flushes the file, returns low/high 32-bit byte counters, ends compression, and frees the wrapper.

Dependencies and interactions:
- Calls `BZ2_bzCompressInit`, `BZ2_bzCompress`, and `BZ2_bzCompressEnd`.
- Uses `bzFile` and `BZ_SETERR` from `bzlib_stdio_private.h`.
- Write buffering uses the same `BZ_MAX_UNUSED` fixed-size buffer as the read side.

Research notes:
- `abandon` skips finishing/flushing and is used by `bzzlib.c` when close after a write error fails.
- Sequence checks prevent writing to read-mode handles.
