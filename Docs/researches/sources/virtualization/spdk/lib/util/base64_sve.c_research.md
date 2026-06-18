# File Research: sources/virtualization/spdk/lib/util/base64_sve.c

This file provides AArch64 SVE acceleration helpers included by `base64.c` when SVE is available.

It implements generic table-lookup helpers for 2, 3, 4, and 8 SVE vectors, selected based on runtime vector length. These helpers combine `svtbl` lookups across table segments and report invalid decode values marked `255`.

`base64_encode_sve()` computes the largest input prefix divisible by three, then handles vector lengths of 16, 32/48, or at least 64 bytes with different table-loading strategies. For each predicate-sized batch, it loads/deinterleaves three input streams, converts 8-bit input bytes into four 6-bit streams, maps those through the selected encoding table, stores four interleaved output streams, and advances caller-owned source/destination/length pointers.

`base64_decode_sve()` similarly handles vector lengths from 16 through 128+ bytes. It loads four encoded streams, rejects input bytes >= 128, maps characters through the decode table using the vector-length-specific helper, rejects invalid decoded values, converts four 6-bit streams into three output byte streams, stores them, and advances pointers.

The functions are void fast paths; invalid decode data causes an early return with the remaining input left for scalar validation in `base64.c`. The implementation assumes the caller has already done Base64 padding and length sanity checks.
