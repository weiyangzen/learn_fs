# File Research: sources/os/linux/linux/fs/fat/fatent.c

## Purpose
Implements low-level FAT table entry access, mutation, free-space allocation, cluster freeing, free-space counting, and trim/discard support for FAT12, FAT16, and FAT32.

## Main Responsibilities
- Provides variant-specific FAT entry operations through `struct fatent_operations`.
- Reads/writes FAT entries, including FAT12 entries that can straddle block boundaries.
- Mirrors primary FAT changes to backup FATs.
- Allocates clusters and links them into chains.
- Frees cluster chains, optionally issuing discard.
- Counts free clusters and updates FAT32 FSINFO state.
- Implements `FITRIM` cluster scanning.

## Key Interfaces
- `fat_ent_access_init()`: selects FAT12/16/32 operations and initializes `fat_lock`.
- `fat_ent_read()` / `fat_ent_write()`: public read/write operations for one FAT entry.
- `fat_alloc_clusters()`: finds free entries, marks them EOF, links multiple allocated clusters, mirrors writes, updates free counts.
- `fat_free_clusters()`: walks a chain, marks entries free, mirrors writes, batches buffer syncing, and optionally discards freed extents.
- `fat_count_free_clusters()`: sequentially scans FAT entries with readahead.
- `fat_trim_fs()`: trims free cluster runs within a requested byte range.

## Important Behavior
FAT12 access uses a global `fat12_entry_lock` around nibble-level read/write because one entry shares bytes with neighbors. FAT16 and FAT32 are aligned pointer accesses, with FAT32 preserving the high reserved nibble on writes.

`fat_alloc_clusters()` holds `sbi->fat_lock` while scanning and modifying free entries. It starts near `prev_free + 1`, wraps at `max_cluster`, updates `prev_free`, decrements `free_clusters` when valid, and rolls back by freeing already allocated clusters if a later sync/mirror error happens.

`fat_free_clusters()` treats encountering a free entry inside a chain as corruption. It updates `free_clusters`, marks FSINFO dirty, and batches mirrored buffer writes to avoid excessive I/O.

`fat_trim_fs()` converts a byte range into cluster indices, scans for free runs meeting `minlen`, handles fatal signals, and temporarily drops `fat_lock` around rescheduling after releasing held FAT buffers.

## Dependencies
Uses geometry and operations from `msdos_sb_info`, buffer-head I/O, block discard helpers, metadata buffer tracking, and logging/sync helpers from `misc.c`.

## Research Notes
This file is the serialization center for FAT table mutations. The public callers rely on `fat_lock` for FAT entry consistency, while higher layers separately protect inode size/chain state.
