# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.h

This small header defines primitive macros used by the HTree half-MD4 hash implementation.

Definitions:
- `F`, `G`, `H`: MD4 Boolean functions.
- `ROTATE_LEFT`: 32-bit left rotation macro.

Dependencies:
- Assumes 32-bit arithmetic operands.

Design notes:
- Used by `ext2fs_hash.c` only for MD4-style hash transformations.
