# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5.c

Implements the MD5 streaming front end and finalization logic. It includes `os.h` and `<libsec.h>`, carries the RSA Data Security MD5 notice, and declares external `_md5block`.

Public `md5(uchar *p, ulong len, uchar *digest, MD5state *s)` allocates and seeds state when needed, fills pending partial blocks, processes full 64-byte blocks via `_md5block`, and either returns state for continued streaming or finalizes with MD5 padding and little-endian length.

The static `encode` helper writes 32-bit words to bytes in little-endian order. The compression function itself is split into `md5block.c`.
