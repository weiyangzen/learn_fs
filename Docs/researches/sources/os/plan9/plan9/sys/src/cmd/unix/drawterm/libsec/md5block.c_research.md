# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5block.c

Contains the MD5 compression function `_md5block(uchar *p, ulong len, u32int *s)`. It includes `os.h` and `<libsec.h>`.

The file defines MD5 logical functions, rotate constants, and the per-round transformation macros. `_md5block` decodes each 64-byte input block into sixteen 32-bit little-endian words, runs the four MD5 rounds, and accumulates the result into the caller’s four-word state.

This file is the hot compression core used by `md5.c`; it does not manage padding, streaming state, or digest output.
