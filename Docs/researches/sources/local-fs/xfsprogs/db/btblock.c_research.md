# File Research: sources/local-fs/xfsprogs/db/btblock.c

Defines field layouts for standalone XFS btree blocks across many btree families: bmap data/attr, inode btrees, finobt, bnobt, cntbt, rmapbt, realtime rmapbt, refcountbt, and realtime refcountbt. It supports legacy and CRC variants where applicable. Generic helpers identify the btree geometry from magic, or coerce from current type if magic is bad, then compute record/key/pointer counts and offsets for leaf vs internal blocks.

The file also defines packed record/key subfield layouts for bmbt, inobt sparse/non-sparse records, alloc btrees, rmap high/low keys and records, and refcount CoW flag fields. `btblock_size` returns filesystem block size in bits. This is central xfs_db schema data; malformed magic can still be viewed through type-based coercion, which is useful for repair/debug sessions but should be understood as interpretive rather than authoritative.
