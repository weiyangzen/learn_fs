# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/crctable.c

Purpose: Defines the 256-entry CRC-32 lookup table used by bzip2.

Key points:
- `BZ2_crc32Table` contains the AUTODIN-II/Ethernet/FDDI style CRC table.
- The table is used by CRC update macros in `bzlib_private.h`.

Dependencies and interactions:
- Included in the bzip2 library build as global data.
- Compression and decompression update block and combined CRCs through this table.

Research notes:
- Static data only. Correctness depends on preserving exact values.
