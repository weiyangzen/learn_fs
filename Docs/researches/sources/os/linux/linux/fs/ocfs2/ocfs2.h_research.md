# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2.h

Role: Main in-kernel OCFS2 runtime header. It pulls in on-disk definitions, ioctl ABI, lock IDs, block checking, reservations, and filecheck state, then defines core runtime structures and inline helpers used across the filesystem.

Key contents:
- Metadata cache abstraction:
  - `OCFS2_CACHE_INFO_MAX_ARRAY`
  - `enum ocfs2_caching_info_flags`
  - `struct ocfs2_caching_info`
  - `ocfs2_metadata_cache_get_super()` prototype
- Cluster node maps via `struct ocfs2_node_map`, limited to 256 nodes.
- Cluster lock machinery:
  - AST/unlock action enums
  - lock resource flags such as `OCFS2_LOCK_ATTACHED`, `BUSY`, `BLOCKED`, `NEEDS_REFRESH`, `QUEUED`, `PENDING`
  - `struct ocfs2_lock_res`, including holders, requested/blocking levels, LVB, wait queue, debug list, optional stats, and lockdep map
- Orphan scan state:
  - `enum ocfs2_orphan_reco_type`
  - `enum ocfs2_orphan_scan_state`
  - `struct ocfs2_orphan_scan`
- Volume, allocation, local allocation, mount option, journal trigger, and recovery-state enums.
- `struct ocfs2_super`, the central mounted filesystem state:
  - superblock/root/system inodes
  - slot info and local/global system inode arrays
  - feature flags, mount options, cluster stack identity
  - generation counters, slot/node identity, cluster/block sizing
  - recovery maps/thread, journal pointer, checkpoint waiters
  - local allocation, reservation maps, truncate log, orphan scan, quota recovery
  - DLM connection and lock resources
  - downconvert thread state, blocked lock list, workqueue
  - sysfs/debug/filecheck state
- `OCFS2_SB(sb)` cast helper.

Important inline behavior:
- Feature checks: sparse allocation, unwritten extents, append DIO, inline data, xattrs, metadata ECC, indexed directories, discontiguous block groups, refcount trees, local mount, extended slot map.
- Link-count helpers read/write 32-bit logical link counts split across low/high 16-bit dinode fields.
- Read-only/emergency helpers atomically update and inspect OSB read-only/error flags.
- Cluster stack helpers distinguish userspace stacks, classic `o2cb`, and global heartbeat.
- Signature validation macros check dinodes, extent blocks, group descriptors, xattr blocks, dir trailers, dx roots/leaves, and refcount blocks.
- Unit conversion helpers translate among bytes, sectors, blocks, clusters, pages, and megabytes.
- Bitmap helpers provide little-endian bit operations and unaligned-bit accessors.

Design notes:
- This file is runtime-oriented, while `ocfs2_fs.h` is format-oriented.
- Most small helpers are deliberately inline because OCFS2 code constantly checks feature bits and performs cluster/block conversions.
- `struct ocfs2_super` is the primary cross-subsystem coupling point for allocation, journaling, DLM, recovery, quota, orphan cleanup, and mount policy.
