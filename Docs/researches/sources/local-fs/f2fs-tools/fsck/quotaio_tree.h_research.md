# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_tree.h

Purpose: defines shared structures and APIs for quota qtree storage.

Key contents:
- Defines in-memory quota ID type `qid_t`.
- Defines tree constants: `QT_TREEOFF`, `QT_TREEDEPTH`, `QT_BLKSIZE_BITS`, and `QT_BLKSIZE`.
- Defines `struct qt_disk_dqdbheader`, the on-disk header for quota data blocks, with a static size assertion of 16 bytes.
- Declares `struct qtree_fmt_operations`, the format-specific callbacks for memory/disk conversion and ID matching.
- Defines `struct qtree_mem_dqinfo`, holding quota file block count, free block list head, free-entry list head, entry size, and format operations.
- Declares qtree read/write/delete/scan utilities.

Important dependencies:
- Included by `dqblk_v2.h`, `quotaio_v2.c`, and `quotaio_tree.c`.
- Uses little-endian F2FS types from `f2fs_fs.h`.

Risk notes:
- The header comment says “vfsv0 quota format,” but this code is used by the VFS v1 implementation in this tree.
