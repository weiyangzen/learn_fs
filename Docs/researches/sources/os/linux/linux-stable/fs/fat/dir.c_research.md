# File Research: sources/os/linux/linux-stable/fs/fat/dir.c

This file implements shared directory handling for FAT-family filesystems, including directory entry iteration, short/long filename parsing, lookup helpers, ioctl readdir variants, entry removal, and entry allocation.

Key responsibilities:
- Walk directory entries with block mapping through `fat_bmap()`.
- Parse VFAT long-name slots and DOS 8.3 entries.
- Convert on-disk names through NLS or UTF-8 rules.
- Implement `iterate_shared` and legacy VFAT readdir ioctls.
- Search directories by name or starting cluster.
- Allocate and initialize directory clusters.
- Add or remove directory entry slots, including multi-slot long names.

Important functions:
- `fat_get_entry()` and `fat__get_entry()` iterate 32-byte directory entries, reading mapped blocks and issuing cluster readahead.
- `fat_parse_long()` reconstructs VFAT long filenames from ordered `ATTR_EXT` slots and validates slot count, checksum, ordering, EOF, volume, and deleted/free states.
- `fat_parse_short()` converts 8.3 entries to display names, respecting hidden-dot behavior, case flags, shortname display policy, and NLS conversion.
- `fat_search_long()` searches by short or long name and returns a `fat_slot_info` describing the matched slot range and on-disk inode position.
- `__fat_readdir()` emits directory entries, fakes root `.` and `..`, handles long/short name selection, and supports ioctl callbacks that return both names.
- `fat_dir_ioctl()` and compat variants implement `VFAT_IOCTL_READDIR_SHORT` and `VFAT_IOCTL_READDIR_BOTH`.
- `fat_scan()` and `fat_scan_logstart()` find entries by formatted 8.3 name or first cluster.
- `fat_dir_empty()` and `fat_subdirs()` scan for directory emptiness and subdirectory counts.
- `fat_alloc_new_dir()` allocates a cluster and initializes `.` and `..`.
- `fat_add_entries()` finds free slots or allocates new clusters, writes long-name slots before the short entry, and returns the final short-entry location.
- `fat_remove_entries()` marks the short entry first as deleted, then removes any preceding long-name slots.

State and integration:
- Uses `struct fat_slot_info` as the common handoff between lookup/namei code and mutation code.
- Uses `sbi->s_lock` for serialized readdir/namei paths.
- Updates directory times, inode version, metadata buffer tracking, and synchronous-directory writes where required.
- Calls into `fat_alloc_clusters()`, `fat_chain_add()`, `fat_free_clusters()`, `fat_sync_inode()`, and FAT time helpers.

Failure behavior:
- Directory read failures are rate-limited and skipped when possible during iteration.
- Corrupt entries or invalid long-name slot chains are ignored for lookup/readdir unless memory or I/O errors occur.
- Entry allocation carefully rolls back newly written free slots when later cluster allocation or chain extension fails.

Research relevance:
- This is the shared namespace storage layer used by both `msdos` and `vfat`; it defines how Linux interprets, scans, creates, and deletes FAT directory records.
