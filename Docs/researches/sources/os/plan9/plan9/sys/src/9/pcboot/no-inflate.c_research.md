# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/no-inflate.c

This tiny file supplies a link-time `gunzip` stub for bootstrap builds that do not include gzip decompression.

Key responsibilities:
- Defines `gunzip` with the expected signature.
- Prints that gzipped kernels are unsupported by this bootstrap.
- Returns `-1` to signal failure.

Filesystem/storage relevance:
- Affects boot image loading behavior only. Kernel images must be uncompressed when this object is linked.
