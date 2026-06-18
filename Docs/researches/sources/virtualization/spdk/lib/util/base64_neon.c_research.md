# File Research: sources/virtualization/spdk/lib/util/base64_neon.c

This file provides AArch64 NEON acceleration helpers included by `base64.c` when SVE is unavailable.

`base64_encode_neon64()` processes 48 input bytes at a time into 64 output bytes. It deinterleaves input with `vld3q_u8`, shifts three input byte streams into four 6-bit streams, uses a 64-byte table lookup to map values to the selected Base64 alphabet, interleaves with `vst4q_u8`, and advances caller-owned source/destination/length pointers.

`base64_decode_neon64()` processes 64 encoded bytes at a time into 48 decoded bytes. It uses two 64-byte lookup tables and NEON table lookup instructions to classify ASCII ranges, rejects chunks with any value greater than 63, converts four 6-bit streams back to three 8-bit streams, stores with `vst3q_u8`, and advances pointers.

The file defines separate standard and URL-safe decode tables arranged for NEON lookup. It has a compile-time guard rejecting non-AArch64 builds and is not compiled as an independent translation unit in this Makefile path.

Key invariant: on invalid input, the NEON decode loop stops without consuming that chunk, leaving scalar decode in `base64.c` to perform final validation and return `-EINVAL`.
