# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtgroup.h

This header declares the incore realtime group abstraction and inline conversion/reference helpers. It is the public libxfs interface used by the realtime bitmap, rmap/refcount btrees, superblock, type verifier, and zoned realtime code.

`enum xfs_rtg_inodes` enumerates per-rtgroup metadata files: allocation bitmap, allocation summary, rmap btree inode, and refcount btree inode. A lockdep assertion ensures the enum count fits lockdep subclass limits when lockdep is available.

`struct xfs_rtgroup` embeds `struct xfs_group`, stores metadata inode pointers indexed by `xfs_rtg_inodes`, records the number of realtime extents in the group, and has a union used either as a realtime summary cache for bitmap-based devices or as the currently open zone object for zoned devices. `rtg_gccount` tracks outstanding zoned-GC activity so an rtgroup with active GC is not selected as a new victim. `XFS_RTG_FREE` is an xarray mark for zoned allocators to identify groups with no written blocks.

The inline accessors convert between generic group and rtgroup objects and expose mount, group number, group block count, and metadata inode slots. Passive references use `xfs_rtgroup_get`, `xfs_rtgroup_hold`, and `xfs_rtgroup_put`; active references use `xfs_rtgroup_grab` and `xfs_rtgroup_rele`. Iteration is provided by `xfs_rtgroup_next_range` and `xfs_rtgroup_next`.

Address conversion helpers map between realtime block numbers, rtgroup numbers, group-relative block numbers, realtime extents, disk addresses, and raw filesystem blocks. `xfs_rtb_to_daddr` and `xfs_daddr_to_rtb` handle the special case of rtgroups without disk-address gaps by translating logical group layout to contiguous hardware layout. `xfs_rtgroup_raw_size` returns the hardware zone/group size and includes zone gaps when present.

Under `CONFIG_XFS_RT`, the header declares rtgroup allocation/free/init, geometry, locking, metadata inode loading/creation/release, realtime superblock update/logging, and `xfs_rtginode_path`. Without realtime support, stubs return no-op values or `-EOPNOTSUPP`.

Notable issue: `xfs_rtginode_irele` is declared twice in the enabled `CONFIG_XFS_RT` block. This is harmless at C declaration level but is duplicated interface noise.
