# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.h

Header for realtime bitmap/summary geometry, word access, and public realtime allocator helpers.

Key contents:
- Defines `struct xfs_rtalloc_args`, bundling rtgroup, mount, transaction, cached bitmap/summary buffers, and cached offsets.
- Provides conversion helpers among realtime extents, realtime blocks, rtgroup-relative blocks, block lengths, and alignment offsets.
- Provides rounding helpers for file offsets and block counts to realtime extent size.
- Maps rt extent numbers to bitmap file block and word offsets.
- Provides word pointer/get/set helpers for bitmap words, handling rtgroup header/bigendian format vs legacy layout.
- Provides summary offset, block, info-word, pointer, get, and add helpers.
- Selects buffer ops with `xfs_rtblock_ops`.
- Defines `struct xfs_rtalloc_rec` and range-query callback type.
- Declares realtime bitmap/summary read, scan, modify, summary, free, query, geometry, initialization, and inode-create APIs under `CONFIG_XFS_RT`.
- Supplies `-ENOSYS` stubs or no-op fallbacks when realtime support is disabled.

Design notes:
- Most geometry helpers optimize power-of-two realtime extent sizes through `m_rtxblklog`, falling back to division/modulo otherwise.
- Header helpers centralize legacy vs rtgroup layout differences so `xfs_rtbitmap.c` can operate mostly on abstracted words and counters.
