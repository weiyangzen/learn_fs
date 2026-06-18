# File Research: sources/virtualization/spdk/lib/util/base64.c

This file implements scalar Base64 and URL-safe Base64 encode/decode, with ARM fast paths included at compile time on AArch64.

The encode path validates non-null destination/source and nonzero length, optionally lets NEON or SVE consume large chunks, then encodes remaining input using big-endian 24-bit groups into four Base64 characters. Tail handling emits `=` padding for one- or two-byte leftovers and null-terminates the destination.

The decode path validates the source string, requires input length to be a nonzero multiple of four, strips up to two trailing padding characters, rejects impossible unpadded lengths where `len % 4 == 1`, and optionally reports decoded length through `spdk_base64_get_decoded_len()`. If `dst` is `NULL`, it returns after length calculation. Otherwise, ARM vector code may consume a prefix, and scalar code decodes full groups using lookup tables, rejects invalid characters marked `255`, and carefully handles the final group without overrunning the caller’s output size.

`spdk_base64_encode()` and `spdk_base64_decode()` use the standard `+/` alphabet. `spdk_base64_urlsafe_encode()` and `spdk_base64_urlsafe_decode()` use `-_`.

Important invariants are caller-provided output sizing, padding validation before decode, scalar validation of any vector-unconsumed tail, and the direct inclusion of `base64_neon.c` or `base64_sve.c` only on AArch64.
