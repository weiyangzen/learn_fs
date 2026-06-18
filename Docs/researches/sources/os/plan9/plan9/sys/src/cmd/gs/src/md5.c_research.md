# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.c

`md5.c` implements MD5 from RFC 1321 using the public interface in `md5.h`. It is an independent L. Peter Deutsch implementation with permissive licensing separate from the normal Ghostscript license header style.

The core `md5_process` routine processes one 64-byte block. It handles little-endian data directly when aligned, copies unaligned little-endian data, and byte-swaps for big-endian CPUs. If `ARCH_IS_BIG_ENDIAN` is not defined, it detects byte order dynamically.

The implementation defines the 64 MD5 constants, Boolean functions, rotation macro, and four MD5 rounds. `md5_init` initializes length and state words, `md5_append` updates bit counts and processes full/partial blocks, and `md5_finish` pads the message, appends the bit length, and writes the 16-byte digest in little-endian order.

Integration in Ghostscript is via `lib.mak` and stream digest support. Security note: MD5 is cryptographically broken for collision resistance, but this implementation is still suitable only for historical compatibility or non-adversarial checksums.
