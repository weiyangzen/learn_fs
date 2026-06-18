# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fsdir.h

## Role

Defines the UFS directory entry disk layout and directory-size/alignment macros.

## Key Definitions

- `DIRBLKSIZ` is `DEV_BSIZE`; directory blocks are intended to be atomically transferable.
- `MAXNAMLEN` is 255.
- `struct direct` stores inode number, record length, name length, and NUL-terminated name buffer.
- `DIRSIZ(dp)` computes the minimum 4-byte-aligned record length needed for a given entry.

## Kernel-Only Helpers

- `struct dirtemplate` models initial `"."` and `".."` directory entries.
- `struct tmp_dir` is a packed reduced directory-entry structure used for manipulation without the full 256-byte name array.

## Semantics

Directories are variable-length records inside fixed directory blocks. Free space is represented by enlarged `d_reclen`; deleted first entries in a block use `d_ino == 0`.

## Risk Notes

Directory update code depends on exact 4-byte alignment and record-length semantics. Miscomputing `DIRSIZ()` or record coalescing can break directory traversal and fsck repair.
