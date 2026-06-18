# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.h

## Purpose
Defines zlib’s private compressor state and internal compression constants.

## Key Elements
Declares literal/length/distance code constants, stream status values, Huffman tree data structures, `Pos`/`IPos`, and the full `deflate_state` structure. Declares tree helper functions and inline tally macros for literals and distance/length pairs.

## Behavior/Risks
The header explicitly warns applications not to include it directly. `deflate_state` owns the sliding window, hash chains, pending output, compression parameters, dynamic Huffman trees, match buffers, heap, and bit buffer. Macro-heavy design ties it tightly to `deflate.c` and `trees.c`, with behavior changing under `DEBUG`, `FASTEST`, `NO_GZIP`, and related compile-time flags.

## Dependencies
Includes `zutil.h` and expects zlib internal types, allocation, and portability macros.
