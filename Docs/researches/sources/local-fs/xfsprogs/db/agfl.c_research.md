# File Research: sources/local-fs/xfsprogs/db/agfl.c

Defines the `agfl` command and AG freelist block field layouts. It supports both non-CRC and CRC AGFL formats: legacy `agfl_flds` presents the block-number array starting at the magic field offset, while `agfl_crc_flds` exposes magic, seqno, uuid, lsn, crc, and then the block-number array after `struct xfs_agfl`. The block-number array length is computed with `libxfs_agfl_size(mp)`.

The command validates an optional AG number, defaults unset `cur_agno` to zero, and positions the cursor at `XFS_AGFL_DADDR` as a sector-sized `TYP_AGFL`. `agfl_size` returns sector size in bits. The next type for freelist block numbers is `TYP_DATA`, allowing block navigation from entries.
