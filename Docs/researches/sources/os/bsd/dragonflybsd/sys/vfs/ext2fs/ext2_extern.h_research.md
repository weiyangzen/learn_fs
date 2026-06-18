# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extern.h

This header declares the cross-file ext2fs API for allocation, mapping, directory operations, inode conversion, htree handling, checksum maintenance, inode hash management, and vnode operations.

Key responsibilities:
- Provide prototypes for ext2 block/inode allocation, freeing, mapping, truncation, and updates.
- Declare directory lookup, readdir, insertion, deletion, rewrite, emptiness, and ancestry checks.
- Declare htree lookup/add/create/hash helpers.
- Declare checksum functions for superblocks, directory blocks, htree nodes, extents, bitmaps, inodes, and group descriptors.
- Declare inode hash functions and vnode allocation.
- Define low-level allocation flags.
- Export vnode operation tables.

Important definitions:
- `BA_CLRBUF`: Caller will not overwrite the full block; newly allocated buffers must be cleared and existing buffers read.
- `BA_SEQMASK`, `BA_SEQSHIFT`, `BA_SEQMAX`: Sequential-read/allocation hint encoding.
- Extern vnode op tables: `ext2_vnodeops`, `ext2_specops`, `ext2_fifoops`.

Important interactions:
- This is the main internal contract among `ext2_alloc.c`, `ext2_balloc.c`, `ext2_bmap.c`, `ext2_csum.c`, `ext2_htree.c`, `ext2_inode.c`, `ext2_inode_cnv.c`, `ext2_lookup.c`, and `ext2_subr.c`.

Notable behavior:
- The header exposes both implemented and stubbed extent entry points, so callers must rely on runtime errors for unsupported extent operations.
