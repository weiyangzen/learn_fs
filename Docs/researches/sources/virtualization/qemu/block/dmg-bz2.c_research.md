# File Research: sources/virtualization/qemu/block/dmg-bz2.c

Optional DMG bzip2 decompression module. It defines `dmg_uncompress_bz2_do()`, initializes a `bz_stream`, decompresses one complete chunk, checks for `BZ_STREAM_END` and exact output length, then tears down the bzip2 stream.

A constructor registers the function by assigning the global `dmg_uncompress_bz2` pointer declared in `dmg.h`. The main DMG driver can operate without this module loaded, but bzip2-compressed chunks will fail when accessed.
