# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/flush.c

Purpose: Implements flush operations for individual files and whole VFAT volumes.

Key routines:
- `VfatFlushFile` flushes cache-manager data for an FCB, treats `STATUS_INVALID_PARAMETER` as success for possibly uninitialized caching, and writes dirty directory entries through `VfatUpdateEntry` under `DirResource`.
- `VfatFlushVolume` flushes all non-directory FCBs first, then directory FCBs, then the FAT file object, and finally sends `IRP_MJ_FLUSH_BUFFERS` to the underlying storage device.
- `VfatFlush` dispatches flush IRPs, rejecting the filesystem control device, and choosing volume flush versus single-file flush based on `FCB_IS_VOLUME`.

Implementation notes:
- Whole-volume flush iterates the VCB FCB list twice to flush file data before directory metadata.
- The FAT file object is flushed under `FatResource`.
- Storage devices that return `STATUS_INVALID_DEVICE_REQUEST` for flush are tolerated and treated as success.

Dependencies and interactions:
- Uses FCB list management from `fcb.c`, dirty-entry writing from `dirwr.c`, cache-manager flush APIs, and lower storage-device IRP dispatch.

Notable limitations:
- Comments note removable-media handling is incomplete; volume flushing does not stop early if media is removed.
