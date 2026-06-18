# File Research: sources/os/linux/linux/fs/ext4/ialloc.c

Implements ext4 inode bitmap handling, inode allocation/freeing, orphan validation, inode counters, and lazy inode-table initialization.

Key behavior:
- `ext4_mark_bitmap_end()` marks unused tail bits in bitmap blocks as allocated.
- `ext4_read_inode_bitmap()` validates inode bitmap block locations, handles uninitialized inode bitmaps, reads bitmap buffers, and verifies checksums.
- `ext4_validate_inode_bitmap()` skips checksum verification during fast-commit replay and marks corrupted bitmap groups on checksum failure.
- `ext4_free_inode()`:
  - validates inode refcount and link count
  - clears inode state before freeing bitmap bits
  - updates inode bitmap, group descriptor counts, directory counts, flex-group counters, checksums, and percpu counters
  - marks suspicious bitmap groups corrupt when needed
- Orlov directory allocator:
  - spreads top-level directories by free inode/free cluster averages and directory counts
  - uses directory-name hash or random start point for top-level directories
  - uses flex_bg packing when enabled
  - falls back to above-average free-inode groups
- Non-directory allocator prefers the parent flex group/block group, then quadratic probing, then linear search.
- No-journal mode avoids recently deleted inodes when their inode-table buffer is still dirty, unless needed to prevent false ENOSPC.
- `ext4_mark_inode_used()` is used by recovery/replay to mark a specific inode allocated, initialize related bitmaps, update descriptor counts, and sync metadata immediately.
- `__ext4_new_inode()`:
  - initializes ownership, project id, fscrypt state, quotas, xattr credits, ACL/security needs, and journal credits
  - chooses a target group from explicit goal, Orlov, or parent locality
  - finds and sets a free inode bitmap bit under group lock
  - initializes block bitmap if needed
  - updates group descriptors, checksums, percpu/flex counters, inode core fields, timestamps, flags, checksum seed, inline-data eligibility, extents, fsync tid, ACLs, security xattrs, encryption context, and quota allocation
  - inserts the inode into the inode hash and handles allocation failure cleanup
- `ext4_orphan_get()` validates orphan-list inode numbers, bitmap allocation state, truncatability, bad-inode state, and next-orphan bounds before returning an orphan inode.
- `ext4_count_free_inodes()` and `ext4_count_dirs()` aggregate group descriptor counters.
- `ext4_init_inode_table()` lazily zeroes unused inode-table blocks, coordinates with allocation via `alloc_sem`, validates unused counts, optionally flushes, and sets `EXT4_BG_INODE_ZEROED`.

Important interactions:
- Shares group descriptor and bitmap corruption state with mballoc/group-info code.
- Fast-commit replay uses `ext4_mark_inode_used()` and bypasses some normal bitmap corruption checks while replay state is active.
- New inode creation ties together quota, fscrypt, xattr, ACL, security, extent initialization, journaling, and flex_bg accounting.
