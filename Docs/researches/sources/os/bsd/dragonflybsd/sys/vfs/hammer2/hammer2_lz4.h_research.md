# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.h

## Purpose
Public header for the HAMMER2-local LZ4 implementation. It exposes only the small safe decompression and limited-output compression API used by the filesystem.

## Interfaces
Exports:
- `int LZ4_decompress_safe(char *source, char *dest, int inputSize, int maxOutputSize);`
- `int LZ4_compress_limitedOutput(char *source, char *dest, int inputSize, int maxOutputSize);`

The header documents that safe decompression never writes past the destination buffer or reads past the input buffer, returning a negative result for malformed or oversized source streams. Limited-output compression returns compressed bytes written or zero if it cannot fit within `maxOutputSize`.

## Integration Notes
The API is C-compatible under C++ via `extern "C"`. HAMMER2 strategy code uses the compressor on writes and safe decompressor on reads for blocks whose blockref method encodes `HAMMER2_COMP_LZ4`.

## Risk Notes
The signatures use mutable `char *` for source even though callers often treat input as read-only, causing `__DECONST` use in kernel callers. This mirrors older LZ4 APIs but is not const-correct.
