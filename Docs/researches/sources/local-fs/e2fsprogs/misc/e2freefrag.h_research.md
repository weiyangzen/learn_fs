# File Research: sources/local-fs/e2fsprogs/misc/e2freefrag.h

## Purpose
Defines shared constants and data structures for `e2freefrag`.

## Contents
- `DEFAULT_CHUNKSIZE`: 1 MiB.
- `MAX_HIST`: 32 histogram buckets.
- `struct free_chunk_histogram`: arrays for free extent counts and block counts per bucket.
- `struct chunk_info`: configured chunk size, derived chunk/block bit counts, free chunk totals, min/max/avg metrics, and histogram.

## Notes
- `chunkbytes == 0` means the default chunk size is used by `init_chunk_info`.
- Histogram units are block counts internally, converted to KB at output time.
