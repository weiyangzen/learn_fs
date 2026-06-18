# File Research: sources/os/linux/linux-stable/fs/ocfs2/extent_map.h

Purpose: Declares the OCFS2 in-memory extent-map structures and block/cluster mapping APIs.

Read coverage: complete file read, 80 lines.

Key contents:
- `struct ocfs2_extent_map_item` stores one cached logical-to-physical extent and flags.
- `struct ocfs2_extent_map` holds a capped LRU-style list of cached mappings.
- `OCFS2_MAX_EXTENT_MAP_ITEMS` limits each inode cache to three entries.
- Declares cluster lookup, xattr lookup, block mapping, FIEMAP, overwrite detection, SEEK_DATA/SEEK_HOLE, virtual block reads, and hole-size helpers.
- Provides inline `ocfs2_read_virt_block()` wrapper for a single virtual block.

Important invariants:
- The cache is a hint, not authoritative; tree mutation paths must invalidate stale ranges.
- `ocfs2_read_virt_block()` rejects a NULL buffer-head pointer before delegating to the multi-block path.

Dependencies:
- Requires OCFS2 extent-record/list types, Linux list heads, inodes, files, buffer heads, and FIEMAP structures.

Risk notes:
- Public mapping APIs encode caller locking assumptions, especially around `ip_alloc_sem`, but the header cannot enforce them.
