# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/crctable.c

Static CRC32 lookup table module for libbzip2. It defines `UInt32 BZ2_crc32Table[256]`, used by `BZ_UPDATE_CRC` in `bzlib_private.h`.

The comment identifies it as an AUTODIN-II/Ethernet/FDDI style 32-bit CRC table, vaguely derived from comp.compression FAQ code. No executable functions are present.
