# File Research: sources/local-fs/kdave-linux/fs/btrfs/defrag.c

Btrfs metadata and file defragmentation implementation, including autodefrag inode queuing, B-tree leaf reallocation, and file extent rewrite selection.

Key responsibilities:
- Maintains an rb-tree of autodefrag inode records keyed by root objectid and inode number, recording transid and extent-size threshold.
- Queues inodes for autodefrag when the mount option is enabled and the filesystem is not closing, merging duplicate records by lowering transid and threshold.
- Picks, removes, and cleans pending autodefrag records under `defrag_inodes_lock`.
- Runs autodefrag in batches by resolving roots/inodes, clearing the in-memory defrag flag, and invoking `btrfs_defrag_file()` with a sector limit.
- Reallocates metadata tree leaves by walking shareable roots and forcing COW of non-nearby child blocks so disk order better matches key order.
- Tracks root defrag progress and maximum key across repeated transactions, returning `-EAGAIN` to continue incremental metadata defrag.
- Provides `btrfs_defrag_root()` loop with transaction boundaries, dirty btree balancing, closing/cancel checks, and `BTRFS_ROOT_DEFRAG_RUNNING` serialization.
- Looks up file extents for defrag without inserting extent maps into the inode cache, optionally using `btrfs_search_forward()` to skip older metadata.
- Filters file defrag targets by holes, inline extents, prealloc extents, generation, writeback marker, delalloc state, size threshold, max extent capacity, compression mode, and adjacency/merge potential.
- Prepares folios for defrag by locking, rejecting untested large folios in non-experimental builds, waiting on ordered extents, reading missing data, and ensuring uptodate state.
- Converts selected ranges to delalloc plus `EXTENT_DEFRAG`, reserves/release delalloc space, dirties relevant folio ranges, and handles compressed/no-compress defrag options.
- Processes files in 256 KiB clusters with readahead, max-sector limits, cancellation checks, inode locking, swapfile rejection, and optional immediate writeback.
- Initializes and destroys the autodefrag inode-record slab cache.

Dependencies:
- Uses Btrfs ctree, disk I/O, transaction, locking, accessors, delalloc space, subpage, file-item, super, compression, extent map, and extent I/O infrastructure.
- Depends on page cache, file readahead, writeback throttling, superblock write guards, rbtrees, slab caches, and signal cancellation via `btrfs_defrag_cancelled()`.

Notable risks:
- Autodefrag records can outlive in-memory inode instances, so runtime inode flags are advisory and duplicate rb-tree detection is required.
- File defrag locks folios and extent ranges, waits for ordered extents, and reserves delalloc space; lock ordering is carefully arranged to avoid deadlocks.
- Target collection intentionally skips delalloc ranges and writeback-marked extents; changing these rules can create deadlocks or unnecessary I/O.
- Metadata defrag only operates on shareable roots and uses forced COW, which changes tree block placement while preserving transactional invariants.
- Compression defrag changes inode `defrag_compress` state while the inode is locked and must clear it at the end.
- Non-experimental builds reject large folios with `-ETXTBSY`, so behavior depends on kernel config and page-cache folio state.
