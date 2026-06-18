# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.h

## Purpose
Primary public header for the ext2fs library. It defines public handle types, core filesystem state, flags, feature support masks, inline helpers, and prototypes for most library modules.

## Core Types and State
- Defines ext2fs scalar types: `ext2_ino_t`, `blk_t`, `blk64_t`, `dgrp_t`, `ext2_off_t`, `ext2_off64_t`, `e2_blkcnt_t`, `ext2_dirhash_t`.
- Declares opaque handles for filesystems, bitmaps, badblocks lists, directory block lists, inode scans, file IO, icounts, xattrs, and extents.
- Defines `struct_ext2_filsys`, the central filesystem handle containing:
  - IO channels.
  - superblock and group descriptors.
  - bitmaps, badblocks, dblist.
  - callback hooks for allocation, directory checks, inode IO.
  - inode cache, image IO, journal IO, MMP state.
  - checksum seed, encoding table, progress ops, allocation-range hooks, and private app data.

## Public API Surface
Prototypes cover:
- Filesystem open, close, flush, duplicate, initialize, rewrite-to-IO.
- Block/inode allocation and allocation statistics.
- Bitmap allocation, resize, compare, range get/set, 64-bit bitmap support.
- Block group descriptor accessors and counters.
- Block iteration and logical-to-physical mapping.
- Directory block IO, directory iteration, htree hashing, linking/unlinking.
- Inode scan/read/write/cache.
- File IO abstraction over inodes.
- Journal creation/device/inode attachment.
- MMP lifecycle.
- Checksum set/verify for superblocks, group descriptors, bitmaps, inodes, dirents, extents, EA blocks, MMP, orphan files.
- Extended attribute read/write/hash/refcount, xattr handle operations, EA inode hash/ref helpers.
- Extent open/get/insert/delete/replace/split/goto/bmap/checksum/count/decode.
- Inline data, orphan file, NLS/casefold, symlink, mkdir, path lookup, badblocks, imager, swap, device size, and utility helpers.

## Inline Helpers
Includes inline memory allocation wrappers, dirty/valid bitmap flags, group-of-block/inode helpers, inode data block counts, htree max records, log/div-ceil functions, dirent name/file-type accessors, inode casts, orphan block helpers, htree level selection, and deletion-time setting.

## Integration
Every file in this group either includes this header directly or indirectly. It is the main public contract for libext2fs consumers and internal modules.

## Risks and Notes
- Public struct fields and function prototypes have ABI/API stability concerns.
- Feature support masks determine whether tools can safely open or modify filesystems with newer ext4 features.
- Inline allocation functions protect against overflow for array allocations.
- Xattr and extent declarations here map directly to implementations in `ext_attr.c` and `extent.c`.
