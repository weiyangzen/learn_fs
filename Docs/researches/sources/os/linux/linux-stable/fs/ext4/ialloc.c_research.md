# File Research: sources/os/linux/linux-stable/fs/ext4/ialloc.c

This file implements ext4 inode allocation, inode freeing, inode bitmap loading/validation, inode placement policy, replay-time inode marking, orphan validation, inode/directory counting, and lazy inode-table zeroing.

Major responsibilities:
- Inode bitmap management:
  - `ext4_mark_bitmap_end()` marks unused tail bits as allocated.
  - `ext4_end_bitmap_read()` completes async bitmap reads.
  - `ext4_read_inode_bitmap()` loads a group’s inode bitmap, initializes uninitialized inode bitmaps, validates bitmap block bounds, and verifies checksums.
  - `ext4_validate_inode_bitmap()` checks checksum validity unless fast-commit replay is active.
- Inode freeing:
  - `ext4_free_inode()` validates refcount/nlink/inode number, clears inode state before freeing the bitmap bit, updates group descriptor free-inode and used-directory counts, updates checksums, updates percpu/flex counters, journals dirty metadata, and marks bitmap corruption on double-free.
- Inode placement:
  - `find_group_orlov()` implements Orlov directory placement, spreading top-level directories and choosing groups/flex groups by free inodes, free clusters, and used directory counts.
  - `find_group_other()` places non-directories near the parent/flex group, then falls back to Orlov or quadratic/linear searches.
  - `get_orlov_stats()` reads group or flex group stats.
- Recently deleted avoidance:
  - `recently_deleted()` checks cached inode table blocks in no-journal mode to avoid quickly reusing recently deleted inodes.
  - `find_inode_bit()` finds a free inode bit, preferring not-recently-deleted candidates but falling back when needed.
- Replay support:
  - `ext4_mark_inode_used()` marks a specific inode allocated, writes/syncs bitmap metadata, initializes block bitmap state if needed, updates group descriptors and checksums, and is used by fast-commit replay.
- New inode creation:
  - `__ext4_new_inode()` performs owner/project/quota setup, fscrypt preparation, journal credit expansion for ACL/security/encryption xattrs, group selection, bitmap bit allocation, group descriptor updates, inode initialization, checksum seed setup, inline-data eligibility, quota allocation, encryption context creation, ACL/security initialization, extent tree initialization, fsync transaction tracking, and dirtying.
- Orphan handling:
  - `ext4_orphan_get()` validates on-disk orphan inode numbers, checks bitmap allocation, loads inode, rejects impossible/bad orphan states, and protects against infinite orphan-list processing.
- Counting:
  - `ext4_count_free_inodes()` sums free inode counts from group descriptors, with optional debug bitmap verification.
  - `ext4_count_dirs()` sums used directory counts.
- Lazy inode-table initialization:
  - `ext4_init_inode_table()` zeros unused inode-table blocks for a group, protects against concurrent allocation with `alloc_sem`, handles partial tables, sets `EXT4_BG_INODE_ZEROED`, updates checksums, and optionally issues a flush barrier.

Important design points:
- Inode bitmap corruption is tracked in mballoc group info so future allocation skips suspicious groups.
- Fast-commit replay bypasses some normal bitmap validation/corruption checks because replay is reconstructing metadata.
- Flex_bg support makes directory and file placement operate on flex groups, then choose a real group inside the flex group.
- New inode setup deliberately initializes owner/quota-related fields early so transaction credit accounting can include later xattr work.
- Encryption xattrs are created before other xattrs to reduce external xattr block use and avoid deduplication.
- New regular files/directories/symlinks use extents when the filesystem supports them.
- Inline data remains possible for eligible new inodes unless DAX/EA-inode flags or mode rules forbid it.

Key invariants:
- Reserved inode numbers in group 0 must never be allocated.
- Bitmap bit allocation is retried under group lock if another thread raced.
- Group descriptor counts, flex counters, percpu counters, bitmap checksums, and group descriptor checksums must stay consistent.
- `insert_inode_locked()` failure is treated as likely bitmap corruption/double allocation.
- Orphan inodes must be allocated in the bitmap and either truncatable or linkless enough not to loop forever.
