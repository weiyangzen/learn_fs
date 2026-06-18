# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1.c

Implements the SHA1 streaming front end and finalization logic. It includes `os.h` and `<libsec.h>`, and declares external `_sha1block`.

Public `sha1(uchar *p, ulong len, uchar *digest, SHA1state *s)` allocates/seeds state, fills partial blocks, processes full 64-byte blocks through `_sha1block`, and either returns state for streaming or finalizes with SHA1 padding and a big-endian bit length.

The static `encode` helper writes 32-bit state words in big-endian order. The compression rounds are split into `sha1block.c`.
