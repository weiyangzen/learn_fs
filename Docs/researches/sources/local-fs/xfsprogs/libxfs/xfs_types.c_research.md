# File Research: sources/local-fs/xfsprogs/libxfs/xfs_types.c

This file implements verifier helpers for fundamental XFS typed numbers: data filesystem blocks, allocation-group blocks, inodes, realtime blocks/extents, inode counts, directory/attribute offsets, and file offsets.

Data-device block verifiers reject block pointers outside the filesystem, outside the AG, or inside static AG metadata. `xfs_verify_agno_agbno` checks AG-local bounds and excludes blocks up to the AGFL block. `xfs_verify_fsbno` converts fsblock to AG and AG block and uses that helper. `xfs_verify_fsbext` checks overflow, both endpoints, and same-AG containment.

Inode verifiers derive AG number and AG inode number, verify round-trip conversion, and check the inode lies within the per-AG valid inode range. `xfs_is_sb_inum` identifies internal superblock-referenced inodes: realtime bitmap, realtime summary, and quota inodes. `xfs_verify_dir_ino` rejects those internal inodes before normal inode validation.

Realtime block verification handles old single-rt-section filesystems and new rtgroups. With rtgroups, it derives rtgroup number and realtime extent number, checks group count, checks the extent against that group's actual extent count, and rejects the reserved realtime superblock area in group 0 when present. `xfs_verify_rtbext` checks overflow, both endpoints, and same-rtgroup containment for rtgroup filesystems.

`xfs_icount_range` computes legal inode-count bounds from per-AG ranges and includes a minimum first chunk for root/rtbitmap/rtsum. `xfs_verify_icount` checks summary counters against that range. `xfs_verify_dablk`, `xfs_verify_fileoff`, and `xfs_verify_fileext` validate directory/attribute and generic file block offsets, including overflow checks for ranges.

This file depends on mount geometry, per-AG iteration, realtime group conversion helpers, realtime group extent counts, and quota/internal inode helpers.
