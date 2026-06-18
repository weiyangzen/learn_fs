# File Research: sources/os/linux/linux/fs/exfat/fatent.c

## Purpose
Implements FAT entry access, FAT mirroring, cluster-chain construction, cluster allocation/freeing, cluster zeroing, chain counting, and block readahead for FAT/bitmap-heavy paths.

## Main Interfaces
- `exfat_ent_get`, `exfat_ent_set`
- `exfat_blk_readahead`
- `exfat_chain_cont_cluster`
- `exfat_free_cluster`, `exfat_alloc_cluster`
- `exfat_find_last_cluster`, `exfat_zeroed_cluster`, `exfat_count_num_clusters`

## Key Data Flow
FAT entry reads and writes translate cluster numbers into FAT sectors and byte offsets. Reads validate content, remap reserved values above bad-cluster to EOF, and reject free/bad/invalid references. Writes optionally cache a buffer head and mirror changes to FAT2 when present.

`exfat_alloc_cluster()` uses the allocation bitmap to find free clusters, sets bits, initializes FAT entries when needed, and preserves `ALLOC_NO_FAT_CHAIN` only while allocation remains physically contiguous. If allocation wraps or becomes non-contiguous, it materializes FAT links with `exfat_chain_cont_cluster()` and switches to `ALLOC_FAT_CHAIN`.

`__exfat_free_cluster()` clears bitmap bits for no-FAT or FAT-chain allocations, optionally discards contiguous freed runs, updates `used_clusters`, and includes loop protection.

## Dependencies
Depends on bitmap helpers from `balloc.c`, buffer-head writes from `misc.c`, cluster conversion macros, block-device discard/sync APIs, and `bitmap_lock`.

## Notable Invariants And Risks
- FAT2 mirroring must stay consistent with FAT1.
- Partial allocation failure rolls back through `__exfat_free_cluster()`.
- Looping FAT chains trigger recovery behavior or filesystem errors.
- Directory-sync inodes influence bitmap/FAT flush timing.
