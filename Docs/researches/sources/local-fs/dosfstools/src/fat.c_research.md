# File Research: sources/local-fs/dosfstools/src/fat.c

FAT table access, repair, ownership tracking, bad-cluster handling, and orphan-chain recovery.

Core functions:
- `get_fat()` decodes FAT12, FAT16, or FAT32 entries. FAT32 preserves high reserved bits separately.
- `release_fat()` frees FAT bytes and cluster owner table.
- `read_fat()` loads FAT data, compares redundant FATs, chooses/repairs a FAT copy, initializes `cluster_owner`, and truncates out-of-range cluster links.
- `set_fat()` updates an entry in memory and queues writes to all FAT copies.
- `bad_cluster()` tests FAT bad-cluster markers.
- `next_cluster()` follows a cluster chain, returning `-1` on EOF and aborting on bad-cluster traversal.
- `cluster_start()` maps a cluster number to byte offset.
- `set_owner()` and `get_owner()` manage cluster-to-`DOS_FILE` ownership used by checker passes.
- `fix_bad()` read-tests unowned clusters and marks unreadable ones bad.
- `reclaim_free()` frees allocated but unowned clusters.
- `reclaim_file()` recovers unowned cluster chains into generated root files, breaking orphan cycles and cross-links.
- `update_free()` recomputes free cluster count and repairs FAT32 FSINFO summary.

Important repair behavior:
- Can use user-selected `fat_table` or choose between first/second FAT.
- Refuses to proceed if FAT corruption is too severe and no usable copy exists.
- Maintains FAT32 reserved high bits when rewriting entries.
- Uses `alloc_rootdir_entry()` to create recovered `FSCK%04dREC` files.

Dependencies:
- `boot.c` for root-entry allocation.
- `check.c` types and owner relationships through `DOS_FILE`.
- `io.c` for all disk I/O.
- `common.c` for choices and fatal errors.

Research notes:
- This file owns the low-level mutation semantics for FAT entries; checker code should use these helpers instead of writing FAT bytes directly.
