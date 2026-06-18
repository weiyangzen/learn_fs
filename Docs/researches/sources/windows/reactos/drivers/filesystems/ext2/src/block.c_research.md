# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/block.c

This file is the driver’s low-level NT block I/O helper layer. It handles MDLs, user-buffer locking, splitting a logical read/write into extents and associated IRPs, synchronous reads, sector-aligned disk reads, device I/O controls, media-removal control, and shutdown forwarding.

Key functions:
- `Ext2CreateMdl`: allocates an MDL for a buffer and either builds it for nonpaged pool or probes/locks pages.
- `Ext2DestroyMdl`: walks and frees an MDL chain, unlocking locked pages first.
- `Ext2LockUserBuffer`: attaches an MDL to an IRP user buffer and probes/locks it.
- `Ext2GetUserBuffer`: returns a system address for the IRP MDL or the raw user buffer.
- `Ext2ReadWriteBlockSyncCompletionRoutine`: completion for synchronous multi-block I/O; frees associated IRP resources, propagates failure to the master IRP, decrements outstanding block count, sets final information, and signals the wait event.
- `Ext2ReadWriteBlockAsyncCompletionRoutine`: completion for asynchronous I/O; propagates failure, updates final byte count and file object flags/current offset, releases any held resource, frees the read/write context, and leaves master completion to the I/O manager.
- `Ext2ReadWriteBlocks`: builds either a direct single-extent IRP path or multiple associated IRPs over an extent chain, sets partial MDLs, completion routines, verify/write-through flags, waits when allowed, and returns `STATUS_PENDING` for async completion.
- `Ext2ReadSync`: builds and sends a synchronous `IRP_MJ_READ` to the target device with optional verify override.
- `Ext2ReadDisk`: aligns arbitrary offset/size reads to sector boundaries, reads into a temporary buffer, and copies out the requested slice.
- `Ext2DiskIoControl`: builds and sends a synchronous device-control IRP.
- `Ext2MediaEjectControlCompletion` and `Ext2MediaEjectControl`: update `VCB_REMOVAL_PREVENTED` and send `IOCTL_DISK_MEDIA_REMOVAL`.
- `Ext2DiskShutDown`: forwards `IRP_MJ_SHUTDOWN` to the target device.

Research notes:
- `Ext2ReadWriteBlocks` is central to file data I/O because it bridges filesystem extents to NT storage IRPs.
- Error cleanup is SEH-based and tries to free any unsubmitted associated IRPs/MDLs.
- Async completion stores `ThreadId`/resource information so a resource acquired by the caller can be released after lower-device completion.
