# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5.h

Purpose: Declares RFC 1321-style MD5 hashing context and routines.

Key definitions:
- `MD5_DIGEST_LENGTH` is 16 bytes.
- `MD5_CTX` stores four-word state, bit count, and a 64-byte buffer union with byte and aligned `uint32_t` views.
- APIs: `MD5Init()`, `MD5Update()`, `MD5Final()`.

Important detail: The buffer union supports realigned input access for implementation efficiency.

Relevance to subset A: General digest utility; may support checksums/legacy formats but is not filesystem-specific here.
