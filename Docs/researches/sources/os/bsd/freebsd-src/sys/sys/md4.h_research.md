# File Research: sources/os/bsd/freebsd-src/sys/sys/md4.h

Defines MD4 context and function prototypes.

Key content:
- `MD4_CTX` contains four-word state, two-word bit count, and 64-byte input buffer.
- Userland symbol names are remapped to `_libmd_*` names unless already defined, avoiding clashes with libcrypto.
- Declares `MD4Init`, `MD4Update`, `MD4Pad`, and `MD4Final`.
- Userland-only convenience APIs: `MD4End`, `MD4Fd`, `MD4FdChunk`, `MD4File`, `MD4FileChunk`, and `MD4Data`.
- Uses RSA-MD license.

Research relevance:
- Provides legacy digest API used by compatibility code and protocols that still require MD4.
- Kernel exposure is limited to core transform/update/final API; file/fd helpers are userland-only.

Cautions:
- MD4 is cryptographically broken; presence here is compatibility, not modern security guidance.
- Include context must provide integer types such as `u_int32_t`.
