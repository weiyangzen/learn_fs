# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_balloc.c

This file allocates physical storage for logical file blocks in non-extent ext2 files. It handles direct blocks, indirect blocks, synchronous initialization of new indirect blocks, and buffer-cache return semantics.

Key responsibilities:
- Allocate or fetch a buffer for a requested logical block.
- Maintain sequential allocation hints used by `ext2_blkpref`.
- Populate direct block pointers in `i_db`.
- Allocate single/double/triple indirect metadata blocks as needed.
- Ensure newly allocated indirect blocks are zeroed and written before being referenced.
- Return existing or newly allocated data buffers, optionally cleared/read according to `BA_CLRBUF`.

Important functions:
- `ext2_balloc`: Main allocator. Rejects negative LBNs, updates sequential hints, dispatches extents to `ext2_ext_balloc`, handles direct block allocation, walks indirect paths from `ext2_getlbns`, allocates missing metadata/data blocks, and writes parent pointer blocks.
- `ext2_ext_balloc`: Stub for extent-backed allocation; currently returns `EINVAL`.

Important interactions:
- Calls `ext2_alloc`, `ext2_blkpref`, `ext2_blkfree`, and `ext2_getlbns`.
- Uses DragonFly buffer-cache calls such as `bread`, `getblk`, `bwrite`, `bdwrite`, and `cluster_read`.
- Works with `BA_CLRBUF`, `BA_SEQMASK`, and `IO_SYNC` flags declared in `ext2_extern.h`.

Notable behavior and risks:
- Extent-mode allocation is not implemented in this file; files with `IN_E4EXTENTS` fail allocation with `EINVAL`.
- If a newly allocated indirect block cannot be written, it is immediately freed to avoid persistent pointers to garbage.
- Direct and indirect block maps cannot store physical blocks above `UINT_MAX`; such allocations return `EFBIG`.
