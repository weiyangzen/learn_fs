# File Research: sources/local-fs/reiserfsprogs/fsck/uobjectid.c

Implements fsck’s temporary object-id map. The map is a sparse array of fixed-size bitmap intervals over 32-bit object IDs; an interval pointer of `NULL` means no IDs are used, `(void *)1` means the whole interval is used, and an allocated bitmap tracks mixed intervals. Each bitmap stores a local `__u16` used count at the tail of the 1024-byte allocation.

Key routines:
- `id_map_init()` allocates the index, marks IDs `0` and `1`, then subtracts ID `0` from the global count so callers can treat `0` as reserved convenience state.
- `id_map_test()` and `id_map_mark()` query and mark IDs, upgrading empty intervals to bitmaps and collapsing full bitmaps to the `(void *)1` sentinel.
- `id_map_alloc()` finds the next free object ID, preferring the first non-full bitmap interval, or the first zero interval after a short scan.
- `id_map_flush()` converts the internal bitmap representation back into the superblock object-id interval array, sets `sb_oid_maxsize` / `sb_oid_cursize`, and handles truncation when the superblock map cannot hold all interval boundaries.

Dependencies are `fsck.h`, `misc_*bit()` helpers, ReiserFS superblock accessors, and `reiserfs_super_block_size()`. The commented-out save/load functions are stale alternate object-id-map serialization code and are not active.
