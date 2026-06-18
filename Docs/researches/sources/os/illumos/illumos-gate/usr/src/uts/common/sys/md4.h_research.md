# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md4.h

Purpose: Declares the RSA MD4 message-digest context and routines.

Key definitions:
- `MD4_DIGEST_LENGTH` is 16 bytes.
- `MD4_CTX` contains four-word state, bit count, and 64-byte input buffer.
- APIs: `MD4Init()`, `MD4Update()`, `MD4Final()`.

Important detail: This is classic MD4 compatibility code; it should be treated as a legacy digest interface, not modern cryptographic security.

Relevance to subset A: General kernel/common utility header.
