# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.c

## Purpose
Kernel-adapted reduced LZ4 implementation used by HAMMER2 for file-data compression and decompression. It provides the public functions declared in `hammer2_lz4.h`: `LZ4_compress_limitedOutput()` and `LZ4_decompress_safe()`.

## Implementation Shape
The file is an older Yann Collet LZ4 source adapted for HAMMER2:
- Uses `MEMORY_USAGE 14`, producing a 16 KiB hash table.
- Uses `HEAPMODE 1`; HAMMER2 allocates the hash table with `kmalloc()` instead of stack allocation.
- Defines little-endian, unaligned-access-oriented read/write helpers and 32/64-bit architecture macros.
- Includes `hammer2_lz4_encoder.h` to instantiate compressor routines.

## Compression Flow
`LZ4_create()` allocates the hash table from a HAMMER2-specific malloc type `C_HASHTABLE`; `LZ4_free()` releases it. `LZ4_compress_limitedOutput()` allocates a context, selects `LZ4_compress64k_heap_limitedOutput()` for inputs below `LZ4_64KLIMIT`, otherwise uses `LZ4_compress_heap_limitedOutput()`, frees the context, and returns compressed size or zero on failure.

## Decompression Flow
`LZ4_decompress_generic()` implements token parsing, literal copying, offset decoding, match-length decoding, overlap copying, and strict input/output bounds checks. `LZ4_decompress_safe()` instantiates it with `endOnInputSize`, no 64 KiB prefix, full decoding, and max output size. Malformed streams return a negative value.

## Dependencies
Includes `hammer2.h`, `hammer2_lz4.h`, and `sys/malloc.h`. It relies on kernel memory allocation and HAMMER2 build context, not a generic userspace runtime.

## Risk Notes
This is low-level pointer arithmetic code. Correctness depends on LZ4 format invariants, endian assumptions, unaligned loads, and the caller supplying valid buffer sizes. HAMMER2 write code prefixes compressed LZ4 data with an `int` compressed size because LZ4 does not carry the original size itself.
