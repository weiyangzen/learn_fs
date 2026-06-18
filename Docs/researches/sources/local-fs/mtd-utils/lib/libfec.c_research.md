# File Research: sources/local-fs/mtd-utils/lib/libfec.c

## Purpose
Implements a standalone forward-error-correction library based on systematic Vandermonde matrices over Galois fields. It is used by the multicast image tooling API declared in `mcast_image.h`.

## Main Entry Points
- `fec_new()` initializes global GF tables on first use, validates `k`/`n`, builds the systematic encoding matrix, and returns a `struct fec_parms`.
- `fec_free()` validates the descriptor magic and frees the encoding matrix.
- `fec_encode()` encodes from an array of source packet pointers.
- `fec_encode_linear()` encodes from one contiguous source buffer.
- `fec_decode()` reconstructs missing original packets in place from any `k` unique packet/index pairs.

## Internal Mechanics
The file generates GF exponent, log, inverse, and optional multiplication tables for `GF_BITS` elements, defaulting to GF(256). Encoding starts from a Vandermonde matrix, inverts the top `k x k` portion, multiplies the lower rows by that inverse, and installs an identity matrix in the upper rows so original packets pass through unchanged.

Decoding first `shuffle()`s packets that already belong in original positions, builds a decode matrix from original rows or encoding rows, inverts that matrix with Gauss-Jordan elimination, then rebuilds missing source packets with GF multiply-add loops.

## Dependencies
Uses only libc headers and the matching public prototypes in `mcast_image.h`. It has optional `TEST`/`DEBUG` timing and consistency code.

## Risks and Notes
Allocation failures abort via `exit(1)` in `my_malloc()`, so callers cannot recover from memory pressure. The global GF tables and `fec_initialized` are lazily initialized without synchronization. The `GF_BITS` validation preprocessor condition uses `&&` where a range check would normally use `||`, so invalid values are not rejected by that directive.
