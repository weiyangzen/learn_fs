# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/cleanup.c

This file implements `IRP_MJ_CLEANUP` handling. Cleanup is the Windows file-object transition where handle state, locks, cache maps, delete-on-close, notifications, and share access are torn down before final close releases object references.

Primary function:
- `Ext2Cleanup(PEXT2_IRP_CONTEXT IrpContext)`

Behavior:
- Ignores cleanup on the filesystem control device and uninitialized VCBs.
- For volume opens, releases volume lock state if this file object owns it, decrements open counts, and removes share access.
- For file opens, acquires the FCB main resource, handles repeated cleanup, validates CCB, decrements VCB/FCB open counts, marks archive attribute after modification, and releases directories through `ext3_release_dir`.
- Updates timestamps and saves inode metadata for modified files when needed.
- Checks oplocks, recomputes fast-I/O state, tracks noncached open counts, and drops byte-range locks via `FsRtlFastUnlockAll`.
- Handles deferred allocation/truncation state from create/setinfo paths (`FCB_ALLOC_IN_CREATE`, `FCB_ALLOC_IN_SETINFO`, `FCB_ALLOC_IN_WRITE`), including cache size updates.
- Removes share access and uninitializes cache maps; flushes/purges cache when the remaining opens are noncached or deletion is pending.
- Handles delete-on-close for regular files, directories, and symlink opens, calling `Ext2DeleteFile` and reporting directory/file removal notifications.
- Completes the IRP or queues it if pending.

Research notes:
- The function carefully tracks `VcbResourceAcquired`, `FcbResourceAcquired`, and `FcbPagingIoResourceAcquired` for SEH cleanup.
- Symlink delete-on-close can redirect deletion from the target FCB/Mcb to `Ccb->SymLink`.
- Cache purge may recursively generate close requests, which explains some lock-order caution also seen in `close.c`.
