# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/cformat.h

This header defines the persistent on-disk format of a `cfs` cache partition.

Key contents:
- Magic values `Amagic` and `Imagic`, bit constants, cache-name length, `Indbno`, and `Notabno`.
- Allocation structures:
  - `Dahdr`: allocation block header with magic, logical block size, cache name, and allocation-block count.
  - `Dalloc`: allocation block header plus bitmap.
- `Dptr`: cached file-data pointer containing file block number, disk block number, and valid byte range within the block.
- `Inode`: qid, cached length, root `Dptr`, and in-use flag.
- Inode structures:
  - `Dihdr`: inode block header.
  - `Dinode`: inode block header plus inode array.

Important details:
- Allocation blocks sit at the beginning of the partition.
- `Dptr` may refer to a direct data block or an indirect pointer block via `Indbno`.
- Valid ranges allow caching partial file blocks and detecting gaps.

Filesystem relevance:
- Direct. This is the disk format for `cfs`’s persistent cache.
