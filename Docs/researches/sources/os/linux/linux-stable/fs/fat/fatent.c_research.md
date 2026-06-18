# File Research: sources/os/linux/linux-stable/fs/fat/fatent.c

This file implements raw FAT table entry access for FAT12, FAT16, and FAT32, plus cluster allocation, cluster freeing, free-space counting, and discard trimming.

Key responsibilities:
- Abstract FAT12/16/32 entry layout behind `struct fatent_operations`.
- Read and write FAT entries, including mirrored FAT copies.
- Allocate new cluster chains.
- Free cluster chains and optionally issue discard.
- Count free clusters with FAT-table readahead.
- Implement `FITRIM` cluster-range trimming.

Important functions:
- `fat_ent_access_init()` selects FAT12, FAT16, or FAT32 operations and initializes `sbi->fat_lock`.
- `fat_ent_read()` validates an entry, maps it to a FAT sector/offset, reuses buffer_heads when possible, and returns the decoded next cluster or EOF.
- `fat_ent_write()` updates an entry, optionally syncs modified buffers, and mirrors changes to backup FATs.
- FAT12 helpers handle 12-bit packed entries that can straddle block boundaries, protected by `fat12_entry_lock`.
- `fat_alloc_clusters()` scans from `prev_free`, links allocated entries into a chain, updates free-cluster accounting, mirrors changes, and rolls back partial allocation on error.
- `fat_free_clusters()` walks a cluster chain, marks entries free, batches dirty buffers, updates FSINFO counters, and optionally discards contiguous freed cluster ranges.
- `fat_count_free_clusters()` scans the FAT with readahead and updates `sbi->free_clusters`.
- `fat_trim_fs()` converts a byte `fstrim_range` into cluster indexes, scans for free extents meeting `minlen`, issues discard, and reports trimmed bytes.

State and locking:
- All FAT table mutation and free-space scans are serialized with `sbi->fat_lock`.
- FSINFO updates are marked dirty via the synthetic `fsinfo_inode`.
- Modified FAT buffers are tracked with `mmb_mark_buffer_dirty()` against `sbi->fat_inode`.

Failure behavior:
- Invalid FAT entry access is reported and returns `-EIO`.
- Read failures are rate-limited.
- Allocation sets `free_clusters = 0` when no space is found.
- `fat_trim_fs()` tolerates `-EOPNOTSUPP` from discard as non-fatal for individual trim attempts.

Research relevance:
- This is the allocator and low-level FAT table engine. Most correctness risks involve FAT12 packed-entry handling, mirrored FAT consistency, free-space accounting, and avoiding partial-chain leaks on allocation failures.
