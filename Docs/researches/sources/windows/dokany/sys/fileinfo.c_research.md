# File Research: sources/windows/dokany/sys/fileinfo.c

Implements `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION` dispatch/completion, including local answers for name/position classes, user-mode metadata requests, cache flushing, rename event construction, FCB rename updates, and file-change notifications.

Key entry points:
- `DokanDispatchQueryInformation()` handles query classes directly where possible and otherwise sends `FILEINFO_CONTEXT` to user mode.
- `DokanCompleteQueryInformation()` copies returned file information to the IRP buffer, updates FCB allocation/file size for standard/all/network-open information, and fills name/delete-pending fields for local consistency.
- `DokanDispatchSetInformation()` validates set-information requests, handles position locally, checks truncation against mapped sections, flushes cache around EOF/rename, builds `SETFILE_CONTEXT`, performs oplock checks, and registers the IRP.
- `DokanCompleteSetInformation()` applies successful delete-pending and rename results to FCB/file-object state and emits directory/file notifications.
- `FillNameInformation()` populates `FILE_NAME_INFORMATION`, including UNC/device path prefixing for network filesystems.
- `FlushFcb()`, `FlushIfDescendant()`, and `FlushAllCachedFcb()` flush and purge cache mappings for files or descendant files before rename-sensitive operations.
- `PopulateRenameEventInformations()` converts Windows rename inputs into Dokan's architecture-neutral rename payload.
- `GetParentDirectoryEndingIndex()` and `IsInSameDirectory()` classify rename notifications as same-directory rename versus remove/add.

Core mechanics:
- `FileNameInformation`, `FileNormalizedNameInformation`, `FilePositionInformation`, and `FileNetworkPhysicalNameInformation` are served in kernel when possible.
- Alternate stream queries are rejected unless `Dcb->UseAltStream` is set.
- User-mode query events include the file information class, requested output buffer length, user context, and FCB filename.
- Set-information events include the original file info buffer or a packed `DOKAN_RENAME_INFORMATION` buffer for rename operations.
- Rename construction handles simple same-directory rename, fully qualified target file objects, relative rename with `RootDirectory`, alternate-stream rename, and trailing slash cleanup.
- Delete-pending state is mirrored between FCB flags and `FileObject->DeletePending` after user mode succeeds.
- Rename completion updates the FCB name through `DokanRenameFcb()` and reports old/new name notifications, or remove/add notifications when crossing directories.

Important invariants:
- FCB locks protect filename reads, metadata changes, and cache flush decisions.
- VCB is locked before FCB during successful rename completion to match create-path lookup locking.
- Truncation is rejected with `STATUS_USER_MAPPED_FILE` when `MmCanFileBeTruncated()` says mapped views prevent it.
- Rename event sizes are dry-run calculated before allocation to avoid overflow.

Filesystem relevance:
- This file is Dokan's main metadata bridge for stat-like queries, size/allocation changes, delete disposition, rename, timestamp/attribute updates, and resulting change notifications.

Notable risks:
- `IsInSameDirectory()` is explicitly case-sensitive even when the mounted filesystem may be case-insensitive.
- Rename handling is structurally complex because Windows exposes multiple rename forms and 32/64-bit incompatible `FILE_RENAME_INFORMATION`.
- Cache purge/flush ordering matters for mapped files and directory subtree renames.
