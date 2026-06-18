# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1block.c

Contains the SHA1 compression function `_sha1block(uchar *p, ulong len, u32int *s)`. It includes `os.h`.

The file expands each 64-byte block into the SHA1 message schedule, runs the 80 SHA1 rounds with the standard round functions/constants, and accumulates into the five-word state supplied by the caller.

It performs only block compression; initialization, padding, length encoding, and digest output are handled by `sha1.c`.
