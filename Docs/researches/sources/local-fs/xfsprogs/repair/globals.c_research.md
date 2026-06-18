# File Research: sources/local-fs/xfsprogs/repair/globals.c

## Role

`globals.c` defines global state shared by xfs_repair phases and helper modules.

## Major State Groups

- Command and device state: filesystem name, file descriptors, external log/realtime names, file/device mode.
- Behavior flags: verbose, no-modify, dangerous repair, zap log, core dump, geometry assumptions, feature additions.
- Runtime buffers and direct I/O sizing.
- Repair status: primary superblock modified, bad inode btree, dirty filesystem, copied stripe unit.
- Required reconstruction flags: root inode, root `..`, metadata root inode, metadata `..`, realtime bitmap/summary inode.
- Superblock counter accumulation: inode counts, free blocks, realtime extents.
- Geometry-derived globals: inodes per block, AG count, chunk sizing, max symlink blocks.
- Parallel/progress state: report interval, progress counters, AG stride, thread count.
- Low-space behavior: `need_packed_btrees`.

## Quota Inode State

The file stores user/group/project quota inode numbers and per-type state:

- Unknown.
- Have.
- Lost.

Helpers provide mutation and queries:

- `set_quota_inode`
- `lose_quota_inode`
- `clear_quota_inode`
- `get_quota_inode`
- `is_quota_inode`
- `is_any_quota_inode`
- `lost_quota_inode`
- `has_quota_inode`

## Notes

`quotino_off` maps quota type to array slot and asserts on invalid types. This keeps the quota inode state compact and uniform across all repair phases.
