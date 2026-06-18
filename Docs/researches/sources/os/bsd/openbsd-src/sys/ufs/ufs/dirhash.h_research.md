# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/dirhash.h

Read completely: 132 lines.

Declares the optional UFS directory hash accelerator used for large directories.

Core definitions:
- Uses open addressing with `DIRHASH_EMPTY` and `DIRHASH_DEL` sentinels and a two-level hash array of directory offsets.
- Tracks per-directory-block free space in `dh_blkfree` and first-free indexes by free-space size to speed creation.
- `struct dirhash` contains its rwlock, hash arrays, slot counts, free-space summaries, sequential lookup optimization state, recycling score, list membership, and global LRU/LFU list linkage.
- Exposes tunables `ufs_mindirhashsize`, `ufs_dirhashmaxmem`, and `ufs_dirhashmem`.
- Declares build, lookup, insert, remove, move, new-block, truncate, free, and consistency-check routines.

Integration and risks:
- Hash memory can be recycled independently from the inode pointer, requiring callers to detect `dh_hash == NULL` and rebuild/fallback.
- Lock ordering is global dirhash list lock before per-dirhash lock.
- Directory mutation paths must keep free-space summaries and offset hashes synchronized.
