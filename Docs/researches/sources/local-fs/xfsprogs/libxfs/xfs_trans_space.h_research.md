# File Research: sources/local-fs/xfsprogs/libxfs/xfs_trans_space.h

This header defines block-space reservation macros and declares operation-specific space reservation helpers.

The macros model worst-case contiguous record capacities and split costs for bmap, rmap, realtime rmap, allocation btrees, directory/attribute trees, inode allocation, growfs, quota allocation, add-attr-fork, attr remove/set, direct I/O allocation, and inode free. Realtime-specific additions include `XFS_MAX_CONTIG_RTRMAPS_PER_BLOCK`, `XFS_RTRMAPADD_SPACE_RES`, and `XFS_NRTRMAPADD_SPACE_RES`, which size blocks needed to add realtime rmap records.

`XFS_OLD_REFLINK_RMAP_MAXLEVELS` preserves the historical rmap maxlevel value of 9 for reflink reservation compatibility. This avoids altering transaction-space and minimum-log calculations for existing filesystems.

The declared functions compute parent pointer, create, mkdir, link, symlink, remove, and rename space reservations at runtime, accounting for mount features such as parent pointers.
