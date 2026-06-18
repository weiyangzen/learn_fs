# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4_encoder.h

## Purpose
Header-included implementation body for the LZ4 compressor. It is designed to be included by `hammer2_lz4.c` after architecture constants and helper macros are defined.

## Interfaces
Declares allocator helpers:
- `LZ4_create()`
- `LZ4_free()`

Declares and implements:
- `LZ4_compress_heap_limitedOutput()`
- `LZ4_compress64k_heap_limitedOutput()`

Both functions take an external hash-table context, source, destination, input size, and max output size.

## Compression Algorithm
The compressor:
- Initializes a hash table sized from `MEMORY_USAGE`.
- Uses 4-byte hash values from `A32(p)` and multiplicative hashing.
- Skips forward adaptively on incompressible data using `SKIPSTRENGTH`.
- Emits LZ4 tokens where high bits encode literal run length and low bits encode match length.
- Writes match offsets as little-endian 16-bit distances.
- Encodes extended literal/match lengths in 255-byte continuation bytes.
- Enforces output bounds before each token/literal/match-length emission; returns zero on overflow.
- Finishes by emitting last literals.

The 64K variant uses `U16` table entries and `CURRENTBASE(base) BYTE* base = ip`; the general variant uses architecture-dependent `HTYPE`.

## Dependencies
Requires macros and types from the including C file: `BYTE`, `U16`, `U32`, `A32`, `LZ4_HASH`, `RUN_MASK`, `ML_MASK`, `LZ4_WRITE_LITTLEENDIAN_16`, `LZ4_BLINDCOPY`, `LZ4_NbCommonBytes`, `MAX_DISTANCE`, `MFLIMIT`, and related constants.

## Risk Notes
This file is not standalone despite its `.h` extension. It intentionally relies on include-time macro context and undefines local macros at the end. Maintenance risk is high if included elsewhere or if macro names collide.
