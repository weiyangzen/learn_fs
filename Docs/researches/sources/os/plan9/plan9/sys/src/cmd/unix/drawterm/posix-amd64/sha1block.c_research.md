# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/sha1block.c

Portable C implementation of `_sha1block`. It processes one or more 64-byte SHA-1 blocks, builds an 80-word message schedule, applies the four SHA-1 round functions/constants, and accumulates into the five-word state.

Duplication note: this file is byte-identical to the `sha1block.c` copies under `posix-arm`, `posix-mips`, `posix-port`, `posix-power`, and `posix-sun4u`.
