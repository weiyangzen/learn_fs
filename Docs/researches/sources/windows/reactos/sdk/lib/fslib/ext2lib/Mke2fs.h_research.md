# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.h

This is the central ext2lib header for ReactOS mke2fs support.

Core contents:
- Pulls in NDK kernel/RTL user-mode definitions and `ext2_fs.h`.
- Defines `SECTOR_SIZE` from `Ext2Sys->DiskGeometry.BytesPerSector`.
- Provides GUID/UUID compatibility typedefs and boolean aliases.
- Defines ext2 bitmap structures and aliases for inode/block bitmaps.
- Defines `EXT2_FILESYS`, the formatter’s in-memory filesystem state: superblock, group descriptors, bitmaps, media handle, disk geometry, partition info, block size, and accounting fields.
- Defines `EXT2_BDL`, a block-description list entry used by inode data I/O.
- Declares the ext2lib APIs implemented across `Disk.c`, `Group.c`, `Inode.c`, `Memory.c`, `Mke2fs.c`, `Super.c`, and `Uuid.c`.

Risk points:
- The `SECTOR_SIZE` macro depends on a local variable name (`Ext2Sys`) being in scope.
- Bitmap prototypes expose generic mutable bitmap pointers without ownership/lifetime guarantees.
- `bool` is aliased to Windows `BOOLEAN`, which can surprise code expecting C99 `bool`.
