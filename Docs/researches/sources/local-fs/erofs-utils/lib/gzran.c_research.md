# File Research: sources/local-fs/erofs-utils/lib/gzran.c

## Purpose
Builds and consumes gzip random-access indexes compatible with AWS SOCI zinfo format, enabling random reads from gzip/zlib streams.

## Main Structures
- `struct erofs_gzran_cutpoint`: 32 KiB window, uncompressed output position, and input bit position.
- `struct erofs_gzran_builder`: streaming inflate state, source buffer, output window, cutpoint list, counters, and span size.
- `struct erofs_gzran_iostream`: vfile wrapper that reads compressed input using zinfo cutpoints.

## Builder Functions
- `erofs_gzran_builder_init()`: initializes zlib inflate with automatic zlib/gzip decoding.
- `erofs_gzran_builder_read()`: inflates up to a 32 KiB window, records cutpoints at block boundaries and span intervals, and supports concatenated gzip streams.
- `erofs_gzran_builder_export_zinfo()`: writes SOCI-compatible zinfo v2 header and checkpoints.
- `erofs_gzran_builder_final()`: ends inflate and frees cutpoints.

## Reader Functions
- `erofs_gzran_zinfo_open()`: parses zinfo v1/v2 buffers and returns an `erofs_vfile`.
- `erofs_gzran_ios_vfpread()`: selects a cutpoint, primes raw inflate if needed, sets dictionary window, skips to requested offset, and fills caller buffer.
- `erofs_gzran_ios_vfclose()`: frees zinfo state.

## Interactions
- Uses `erofs_vfile` operations and zlib.
- Compiled with functional support only under `HAVE_ZLIB`; otherwise stubs return `-EOPNOTSUPP` or no-op success.

## Notes
The reader creates a virtual uncompressed stream over a compressed input plus zinfo checkpoints.
