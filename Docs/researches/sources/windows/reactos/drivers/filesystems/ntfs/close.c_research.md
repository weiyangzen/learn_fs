# File Research: sources/windows/reactos/drivers/filesystems/ntfs/close.c

Read status: complete file, 123 lines.

This file handles `IRP_MJ_CLOSE` and releases per-open NTFS state.

Key entry points:
- `NtfsCloseFile()` reads the CCB and FCB from the file object, exits early if no CCB is attached, clears `FsContext`, `FsContext2`, and `SectionObjectPointer`, decrements the VCB open handle count, releases the FCB for normal externally-created file objects, frees any directory search pattern, then frees the CCB.
- `NtfsClose()` ignores close on the global filesystem device object, otherwise acquires `DeviceExtension->DirResource`, calls `NtfsCloseFile()`, releases the resource, and queues if needed.

Important dependencies:
- FCB reference management in `fcb.c`.
- Directory enumeration state stored in `Ccb->DirectorySearchPattern`.
- The create path's `NtfsAttachFCBToFileObject()` allocation of CCBs.

Notable behavior and risks:
- Stream file objects created internally have no `FileName.Buffer`, so their FCB is not released through the normal external-object branch.
- `DeviceExt->OpenHandleCount` is decremented only when a CCB is present.
- The `DeviceExt` parameter in `NtfsCloseFile()` is used for handle accounting and FCB release, but close correctness depends on file objects being attached consistently by create/open paths.
