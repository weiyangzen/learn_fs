# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_balloc.c

This file allocates or fetches buffers for logical file blocks. It supports both ext4 extent-backed files and classic ext2 direct/single/double/triple indirect block maps.

Key responsibilities:
- Convert a logical block request into an allocated physical block and returned buffer.
- Maintain sequential allocation hints used by `ext2_blkpref`.
- Allocate direct blocks, indirect metadata blocks, and indirect-referenced data blocks.
- Zero and synchronously write newly allocated indirect metadata before linking it from parent pointers.
- Honor `BA_CLRBUF`, `BA_SEQMASK`, and `IO_SYNC` buffer semantics.
- Dispatch extent-backed files to the extent allocator.

Important functions:
- `ext2_ext_balloc`: Uses `ext4_ext_get_blocks` to map/allocate extent-backed blocks, then returns a vnode buffer or reads existing contents.
- `ext2_balloc`: Main classic allocator. Handles direct blocks first, then uses `ext2_getlbns` to walk/allocate indirect chains and final data blocks.

Important interactions:
- Calls `ext2_alloc`, `ext2_blkpref`, `ext2_blkfree`, `ext2_getlbns`, `ext4_ext_get_blocks`, `bread`, `getblk`, `bwrite`, `bdwrite`, and `cluster_read`.
- Updates inode block arrays and inode change/update flags when new pointers are installed.

Notable risks:
- Classic indirect maps store 32-bit block numbers, so newly allocated blocks above `UINT_MAX` return `EFBIG`.
- Error paths after high-block allocation should be audited because allocation has already occurred before the 32-bit compatibility check.
