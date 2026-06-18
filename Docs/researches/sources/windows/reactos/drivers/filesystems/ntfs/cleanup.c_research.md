# File Research: sources/windows/reactos/drivers/filesystems/ntfs/cleanup.c

Read status: complete file, 126 lines.

This file handles `IRP_MJ_CLEANUP`, separating per-file cleanup from dispatch-level resource acquisition.

Key entry points:
- `NtfsCleanupFile()` gets the FCB from `FileObject->FsContext`. Volume FCBs only decrement `OpenHandleCount`. Non-volume FCBs acquire `MainResource`, decrement `OpenHandleCount`, call `CcUninitializeCacheMap()`, set `FO_CLEANUP_COMPLETE`, and release the resource.
- `NtfsCleanup()` ignores cleanup against the global filesystem device object, otherwise acquires `DeviceExtension->DirResource`, calls `NtfsCleanupFile()`, releases the directory resource, and queues the IRP context if locking could not wait.

Important dependencies:
- FCB state from create/open paths.
- Cache manager cleanup through `CcUninitializeCacheMap`.
- Dispatch queueing through `NtfsMarkIrpContextForQueue`.

Notable behavior and risks:
- Share-access removal is left as a TODO in both volume and file cases.
- Non-volume cleanup requires both the VCB directory resource and the FCB main resource.
- Volume cleanup decrements the volume FCB open count without taking the FCB main resource.
