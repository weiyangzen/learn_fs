# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/write.c

This file implements Ext2 write dispatch for volumes, files, inode extents, MDL completion, deferred Cache Manager writes, and floppy delayed flushes.

`Ext2WriteVolume` handles raw volume writes. Cached writes use `CcPrepareMdlWrite` or `CcCopyWrite`; noncached writes lock caller buffers and write extents directly. Paging writes consult VCB dirty extent tracking to write only tracked dirty ranges and remove them after success.

`Ext2WriteInode` builds extent chains with allocation enabled for non-directory writes, then either dispatches direct block I/O through `Ext2ReadWriteBlocks` or writes buffered data with `Ext2SaveBuffer`.

`Ext2WriteFile` is the main file write path. It validates file type, deletion state, access, byte alignment, locks, oplocks, cacheability, paging I/O, and recursive write-through. It expands allocation and file size when needed, updates inode size, enables the ext large-file feature if required, zeroes gaps before writes beyond valid data length, updates VDL, reports notify changes, and marks file/FCB modified.

`Ext2WriteComplete` completes MDL writes with `CcMdlWriteComplete`. `Ext2Write` rejects writes to the filesystem device, read-only volumes, locked volumes by non-lock owners, and dismount-pending FCB writes before dispatching to volume or file write handlers.

Research notes: the file-size growth path uses a temporary `MajorFunction += IRP_MJ_MAXIMUM_FUNCTION` protocol to influence `Ext2ExpandFile`, which is fragile but intentionally reverted in the finally block. Several error paths call `DbgBreak`, so checked builds may break on operational failures.
