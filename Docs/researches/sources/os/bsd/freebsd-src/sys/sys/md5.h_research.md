# File Research: sources/os/bsd/freebsd-src/sys/sys/md5.h

Defines MD5 context, digest constants, and function prototypes.

Key content:
- Constants:
  - `MD5_BLOCK_LENGTH` = 64
  - `MD5_DIGEST_LENGTH` = 16
  - `MD5_DIGEST_STRING_LENGTH` = 33
- `MD5_CTX` contains four-word state, two-word bit count, and 64-byte input buffer.
- Userland symbol names are remapped to `_libmd_*` to avoid libcrypto collisions.
- Declares `MD5Init`, `MD5Update`, and `MD5Final`.
- Userland-only helpers include `MD5End`, `MD5Fd`, `MD5FdChunk`, `MD5File`, `MD5FileChunk`, and `MD5Data`.
- Uses RSA-MD license.

Research relevance:
- Legacy checksum/digest API used in compatibility and non-cryptographic contexts.
- Some filesystems/tools historically use MD5 for identifiers or integrity checks, so this ABI may appear in related code.

Cautions:
- MD5 is not suitable for collision-resistant security.
- Kernel API omits userland file/fd convenience wrappers.
