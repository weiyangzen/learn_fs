# File Research: sources/virtualization/guestfs-tools/gnulib/lib/bitrotate.h

Inline bit-rotation helpers for unsigned integer types.

Functions:
- `rotl64`, `rotr64` when `UINT64_MAX` exists.
- `rotl32`, `rotr32`.
- `rotl_sz`, `rotr_sz`.
- `rotl16`, `rotr16`.
- `rotl8`, `rotr8`.

Research relevance: small utility used by the hash table’s pointer hashing path.
