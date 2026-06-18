# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_util.h

Declares kernel-only bmap utility interfaces used outside `xfs_bmap_util.c`.

Key elements:
- Declares realtime allocation helper `xfs_bmap_rtalloc`, with a non-RT stub returning `-EFSCORRUPTED`.
- Declares delayed allocation punching and getbmap support.
- Defines `struct kgetbmap`, the in-kernel getbmap output record.
- Declares selected `xfs_bmap.c` helpers needed by bmap utility code.
- Declares preallocation, hole punching, collapse range, insert range, EOF block cleanup, swap extents, block conversion, extent counting, and unmap-range flushing APIs.

Dependencies:
- Shared with ioctl, inode, writeback, and bmap code paths.

Research notes:
- The non-RT `xfs_bmap_rtalloc` stub treats attempts to allocate RT extents without RT support as corruption.
- Header keeps the higher-level bmap operations separate from lower-level bmap implementation internals.
