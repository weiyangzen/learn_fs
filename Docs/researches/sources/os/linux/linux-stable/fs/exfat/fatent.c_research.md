# File Research: sources/os/linux/linux-stable/fs/exfat/fatent.c

This file manages FAT entry I/O, mirrored FAT updates, readahead, cluster-chain construction, allocation, freeing, discard, zeroing, and cluster counting.

Key elements:
- `exfat_ent_get()` validates FAT entry location/content, reads the FAT sector, returns the next cluster, and maps reserved high values to EOF.
- `exfat_ent_set()` writes a FAT entry; lower helper `__exfat_ent_set()` supports cached buffer-head reuse.
- `exfat_mirror_bh()` mirrors FAT sector updates to FAT2 when a second FAT exists.
- `exfat_blk_readahead()` issues block readahead in plugged batches.
- `exfat_chain_cont_cluster()` writes a contiguous FAT chain ending in `EXFAT_EOF_CLUSTER`.
- `exfat_free_cluster()` clears bitmap bits for either contiguous no-FAT chains or FAT chains, optionally issues discard, updates `used_clusters`, and detects loop-like chains.
- `exfat_find_last_cluster()` locates and validates the last cluster of a chain.
- `exfat_zeroed_cluster()` zeroes every block in a newly allocated directory cluster.
- `exfat_alloc_cluster()` finds free bitmap bits, marks them allocated, writes FAT entries when needed, converts no-FAT chains to FAT chains when allocation is no longer contiguous, and updates `clu_srch_ptr`/`used_clusters`.
- `exfat_count_num_clusters()` counts a chain’s length with loop detection.

Important dependencies:
- Uses bitmap helpers from `balloc.c`.
- Used by `inode.c` block mapping, `file.c` truncation/expansion, `namei.c` directory growth, and `dir.c` chain traversal.
- Uses `exfat_update_bh()` from `misc.c` and geometry helpers from `exfat_fs.h`.

Failure/edge behavior:
- Invalid FAT access is reported through rate-limited filesystem errors.
- Allocation rollback calls internal free on partially allocated chains.
- If contiguous allocation fails while `ALLOC_NO_FAT_CHAIN` was expected, it materializes a FAT chain and switches flags.
- Discard unsupported errors disable the discard mount option.
