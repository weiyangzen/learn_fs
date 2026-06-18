# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/read.c

This file implements Ext2 read dispatch for volume objects, regular files, inode extent reads, and MDL read completion.

`Ext2ReadVolume` handles raw volume reads. Cached reads use `CcMdlRead` or `CcCopyRead` against `Vcb->Volume`; noncached reads align length to sector size, lock the user buffer, create a single `EXT2_EXTENT`, and call `Ext2ReadWriteBlocks`.

`Ext2ReadInode` is the lower-level inode read helper. It handles fast symlink data stored inside the inode, builds extent chains with `Ext2BuildExtents`, zero-fills sparse gaps, then either dispatches direct I/O through `Ext2ReadWriteBlocks` or uses `CcCopyRead` from the volume stream.

`Ext2ReadFile` validates file state, lock state, byte ranges, oplocks, cache maps, EOF/VDL behavior, and resource acquisition. Cached reads use Cache Manager APIs; noncached reads lock buffers and call `Ext2ReadInode`.

`Ext2ReadComplete` finalizes MDL reads with `CcMdlReadComplete`. `Ext2Read` is the top-level dispatcher choosing completion, volume read, or FCB read.

Research notes: direct file read buffer locking uses `IoReadAccess` before filling the caller buffer, while volume direct reads use `IoWriteAccess`; this difference is worth verifying against the driver's `Ext2LockUserBuffer` semantics.
