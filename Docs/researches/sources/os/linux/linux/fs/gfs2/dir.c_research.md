# File Research: sources/os/linux/linux/fs/gfs2/dir.c

Implements GFS2 directory storage, lookup, insertion, deletion, readdir, extendible hashing, hash-table caching, leaf splitting/chaining, and exhash deallocation.

Major concepts:
- Linear/stuffed directories store dirents inside the dinode.
- Exhash directories store a directory file containing 64-bit leaf block pointers; leaf blocks contain dirents.
- Hash table entries can point to the same leaf; leaf depth controls how many hash slots reference a leaf.
- At maximum depth, full leaves chain via `lf_next`.

Key entry points:
- `gfs2_dir_get_new_buffer()`
- `gfs2_dir_hash_inval()`
- `gfs2_dir_read()`
- `gfs2_dir_search()`
- `gfs2_dir_check()`
- `gfs2_dir_add()`
- `gfs2_dir_del()`
- `gfs2_dir_mvino()`
- `gfs2_dir_exhash_dealloc()`
- `gfs2_diradd_alloc_required()`

Important control flow:
- Directory data I/O uses `gfs2_dir_write_data()` / `gfs2_dir_read_data()`; stuffed directories use dinode payload, exhash hash tables use journaled directory data blocks.
- `gfs2_dir_get_hash_table()` lazily reads and caches the exhash table, validating that file size matches `2^i_depth * sizeof(__be64)`.
- `gfs2_dirent_scan()` validates record lengths, alignment, block bounds, sentinel rules, and then applies scan callbacks for find, previous, last, space, offset, and gather operations.
- `gfs2_dir_search()` finds a dirent and returns the target inode through `gfs2_inode_lookup()`.
- `gfs2_dir_add()` first uses saved allocation search state if available; otherwise it finds free dirent space, converts linear directories to exhash, splits leaves, doubles hash table depth, or appends chained leaves.
- `dir_make_exhash()` converts stuffed directory contents into a leaf and replaces dinode payload with the initial hash pointer table.
- `dir_split_leaf()` allocates a new leaf, rewrites half the hash pointers, and redistributes entries based on hash divider.
- `dir_double_exhash()` doubles the hash table by duplicating each pointer and increments directory depth.
- `gfs2_dir_read()` gathers dirents, computes stable cookies, sorts hash collisions, and emits entries through `dir_emit()`.
- `gfs2_dir_exhash_dealloc()` walks hash slots and frees leaf chains via `leaf_dealloc()`.

Dependencies and integration:
- Uses bmap allocation/extent helpers, metadata I/O, transactions, resource groups, quota, glocks, VFS dir_context, and GFS2 on-disk directory/leaf formats.

Risks and invariants:
- Corrupt dirent counts, bad record lengths, wrong metatypes, invalid hash-table size, zero inode sentinels in non-first entries, and impossible split geometry trigger consistency errors or `-EIO`.
- Hash cache must be invalidated before hash-table rewrites.
- `gfs2_diradd_alloc_required()` can save a buffer/dirent for later insertion; callers must release through `gfs2_dir_no_add()` if not used.
