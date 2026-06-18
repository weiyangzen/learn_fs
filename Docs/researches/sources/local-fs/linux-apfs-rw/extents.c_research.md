# File Research: sources/local-fs/linux-apfs-rw/extents.c

This file implements APFS file/data-stream extent mapping, allocation, truncation, sparse holes, physical extent reference tracking, cloning, and nonsparse dstream reads.

Read mapping:
- `apfs_extent_from_query()` decodes logical extent records from either the catalog tree or sealed-volume fext tree.
- `apfs_extent_read()` locates and caches the extent covering a logical dstream block.
- `apfs_logic_to_phys_bno()` converts logical block to physical block, returning zero for holes.
- `__apfs_get_block()` maps existing extents to buffer heads for read paths without taking locks; `apfs_get_block()` wraps it under `nx_big_sem`.

Dirty extent cache/write allocation:
- Newly allocated blocks are initially accumulated in `ds_cached_ext` and marked dirty.
- `apfs_dstream_get_new_block()` allocates a physical block, maps/join buffers to the transaction, handles zeroing for new/stale partial blocks, checks whether the cached extent overlaps snapshots, creates sparse holes when extending beyond EOF, and flushes or extends the dirty cache as needed.
- `apfs_flush_extent_cache()` writes the dirty logical extent and physical extent records.

Logical extent updates:
- Extents can be shrunk at head or tail, split, replaced, or inserted.
- Tail updates handle append/growth and replacement of the last extent.
- Mid-file updates are restricted to single-block extents and carefully handle replacing holes, shrinking existing extents, and splitting extents around the new block.
- Sparse hole records use physical block zero and update `ds_sparse_bytes`.

Physical extent-reference tree:
- Physical extents are decoded with `apfs_phys_ext_from_query()`.
- New physical extents are inserted or extended where possible.
- Reference changes split physical extent records at range boundaries, then increment/decrement refcounts.
- Dropping the last reference removes the physical extent record and, for new extents, returns blocks to the free queue and updates volume allocation/free counters.
- Snapshot overlap detection conservatively forces copy-on-write when needed.

Truncation/deletion:
- `apfs_truncate()` flushes cached extents, invalidates the cache, shrinks for smaller sizes, or creates hole extents for larger sparse growth after zeroing the old tail.
- `apfs_shrink_dstream_last_extent()` repeatedly removes or shrinks tail extents until the target size is reached.
- `apfs_inode_delete_front()` deletes as many leading extents as possible, stopping with `-EAGAIN` when the free queue grows too full.

Clone/remap:
- `apfs_remap_file_range()` / `apfs_clone_file_range()` only supports whole-file clone replacement into a freshly created destination.
- It rejects self-clones, partial ranges, compressed/existing dstream targets, and targets with certain xfields.
- Cloning shares the source dstream id, increments the dstream refcount, marks source/destination shared, copies inode flags/size/key class, and forces a transaction commit to make future source writes CoW.
- `apfs_clone_extents()` can create logical extent records under a new dstream id and increment physical references.

Nonsparse dstream helpers:
- `apfs_nonsparse_dstream_read()` reads exact byte ranges from dstreams expected to have no holes, issuing buffer reads and copying requested slices.
- `apfs_nonsparse_dstream_preread()` submits asynchronous reads for all blocks, used by compression/resource-fork paths.

Research relevance: this is the core APFS data-block management layer. It connects logical file extents, physical block allocation, snapshot/clone reference counts, sparse files, truncation, and Linux buffer-head mapping.
