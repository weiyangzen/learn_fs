# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/cleanup.c

This file implements VFAT `IRP_MJ_CLEANUP` handling, which runs when a handle is closed but before the final file-object close release.

Key functions:
- `VfatCleanupFile`
  - Retrieves the FCB from `FileObject->FsContext`.
  - For volume opens, decrements FCB/device open-handle counts and removes share access when other opens remain.
  - For file/directory opens:
    - Acquires FCB main and paging resources exclusively.
    - Converts CCB delete-on-close into `FCB_DELETE_PENDING`.
    - Calls `FsRtlNotifyCleanup`.
    - Decrements open-handle counts.
    - Releases byte-range locks held by the requestor process.
    - Updates the directory entry when `FCB_IS_DIRTY`.
    - For delete-pending last opens, rejects deletion of non-empty directories; otherwise uninitializes the cached stream, clears sizes, and later deletes the directory entry.
    - Calls `CcUninitializeCacheMap` for the current file object.
    - Reports file/directory removal notifications when deletion succeeds.
    - Removes share access when handles remain.
    - Marks `FO_CLEANUP_COMPLETE` and, in KDBG builds, `FCB_CLEANED_UP`.
  - Contains disabled delayed-close logic because comments say it caused filesystem corruption and test failures.
  - Optionally checks for dismount under `ENABLE_SWAPOUT`.
- `VfatCleanup`
  - Returns success immediately for the global filesystem device object.
  - Acquires the volume directory resource, calls `VfatCleanupFile`, releases it unless the device was deleted, clears IRP information, and returns success.

Notable design points:
- Cleanup is where delete-on-close becomes actual deletion if the final open handle is gone.
- Cache uninitialization is deliberately done even if caching may not have been initialized.
- The active implementation avoids delayed close in cleanup; delayed close is handled in the close path instead.
