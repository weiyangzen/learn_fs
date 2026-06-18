# File Research: sources/local-fs/xfsprogs/db/inode.h

## Purpose
Publishes inode field descriptors and inode-specific helpers to the rest of xfs_db.

## Interfaces
- Declares inode field tables consumed by type definitions and print/fuzz code.
- Declares enum printers, fork sizing helpers, inode command initialization, next-type inference, inode sizing, CRC recalculation, and `set_cur_inode()`.

## Dependencies
Requires xfs_db field/type definitions and libxfs inode buffer types.
