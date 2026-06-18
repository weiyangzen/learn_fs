# File Research: sources/windows/winfsp/src/sys/fileinfo.c

## Role

Implements `IRP_MJ_QUERY_INFORMATION`, `IRP_MJ_SET_INFORMATION`, and fast I/O query paths for WinFsp filesystem volumes. It translates Windows `FILE_INFORMATION_CLASS` requests into local cached responses or user-mode WinFsp transactions, updates file-node state on completion, and handles disposition and rename semantics.

## Query Information

The query side supports:

- `FileAllInformation`
- `FileAttributeTagInformation`
- `FileBasicInformation`
- `FileEaInformation`
- `FileInternalInformation`
- `FileNameInformation`
- `FileNormalizedNameInformation`
- `FileNetworkOpenInformation`
- `FilePositionInformation`
- `FileStandardInformation`
- `FileStreamInformation`
- `FileStatInformation` and `FileStatLxInformation` when WSL features are enabled

Unsupported or rejected classes include compression, hard links, alternate short names, and invalid defaults.

The small `FspFsvolQuery*Information` helpers write specific Windows structures into the caller buffer, handling buffer-too-small/overflow behavior. `FileAllInformation` has a two-phase path: first validates/fills name data, then later overlays cached or returned file info.

For most metadata classes, `FspFsvolQueryInformation` first validates output space, acquires the file node, and tries `FspFileNodeTryGetFileInfo`. If cached file info is valid, it fills the buffer synchronously. Otherwise it posts `FspFsctlTransactQueryInformationKind` to user mode, saves request context including the file node and all-information state, and releases owner locks on completion.

`FileStreamInformation` has a separate stream-info cache. `FspFsvolQueryStreamInformationCopy` converts WinFsp `FSP_FSCTL_STREAM_INFO` records into Windows `FILE_STREAM_INFORMATION`, appending `:$DATA`, setting `NextEntryOffset`, and returning overflow when only partial stream names fit.

`FileStatLxInformation` also queries Linux metadata EAs `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` through `FspSendQueryEaIrp` when extended attributes are enabled.

## Set Information

The set side supports:

- `FileAllocationInformation`
- `FileBasicInformation`
- `FileEndOfFileInformation`
- `FilePositionInformation`
- `FileDispositionInformation`
- `FileDispositionInformationEx`
- `FileRenameInformation`
- `FileRenameInformationEx`

It rejects hard links, valid data length, unsupported POSIX variants when the volume does not advertise support, and invalid lengths.

Allocation and EOF setters validate truncation with `MmCanFileBeTruncated`, populate the user-mode request, and on successful response update file info, mark `FO_FILE_MODIFIED`, and notify size changes.

Basic information validates attributes, strips/forces normal and directory bits appropriately, maps `-1` timestamp values to “do not update” zero fields in the WinFsp request, and on completion updates file info, per-handle metadata flags, `FO_TEMPORARY_FILE`, and change notifications.

Position information is handled locally by setting `FileObject->CurrentByteOffset` under the main resource.

Disposition handling performs delete-pending setup. It supports classic and extended disposition flags, rejects root deletion, blocks already POSIX-deleted nodes, checks oplocks, checks image sections with `MmFlushImageSection`, optimizes repeated Windows 10/11 POSIX-delete retry patterns through `FileDesc->DispositionStatus`, and can avoid posting to user mode when `PostDispositionWhenNecessaryOnly` allows a local readonly/cached check. Successful completion updates file-node and file-object delete-pending state and notifies delete-pending directories.

Rename handling validates target names, rejects root and stream rename, optionally captures a subject security context for replace-if-exists, acquires the volume rename resource and file-node resources, uses `FspFileNodeRenameCheck` for old and new names, posts the rename to user mode, and on success emits old/new rename notifications and calls `FspFileNodeRename` to rewrite in-memory descendant names.

`FspFsvolSetInformationPrepare` converts a captured replace-if-exists subject context into a user-mode impersonation token handle and packs the originating process id plus handle into the request. The request finalizer closes this token in the correct process context, releases subject contexts, file-node locks, and the volume rename resource.

## Completion And Retry Model

Query and stream-query completions validate response buffers, save current cache change numbers, release owner-held file-node resources, then try to reacquire exclusive access. If reacquisition fails, they save the response in the IRP request and ask the IOQ to retry completion later. If reacquisition succeeds, they set file/stream info only when the change number still matches; otherwise they use existing cache or response data without overwriting newer state.

Set completions special-case failed disposition requests to store retry status. Successful disposition and rename use dedicated completion helpers; allocation/basic/EOF use the same helper triplets as preparation, with `Response` non-null.

## Fast I/O

`FspFastIoQueryBasicInfo`, `FspFastIoQueryStandardInfo`, and `FspFastIoQueryNetworkOpenInfo` opportunistically answer from valid file-node cached info when the main resource can be acquired. `FspFastIoQueryOpen` supports kernel-mode opens only when `AllowOpenInKernelMode` is set, rejects relative opens, and looks up cached file info by name with access checks.

## Integration Points

This file is the metadata bridge between Windows IRPs and user-mode filesystem transactions. It relies on `file.c` for node locks, cached metadata, rename checks, notifications, and file-info mutation; on `iop.c` for request creation/retry/finalization; on `security.c`/send helpers for security and EA queries; and on volume parameters for feature switches.

## Edge Cases And Risks

- Several information classes are identified by numeric constants `68` and `70`, indicating compatibility with headers where names may not exist.
- Rename and disposition semantics mirror NTFS/FastFat behavior with documented Windows quirks around POSIX delete retries and readonly deletion documentation mismatches.
- User-mode response buffers are bounds-checked before use; stream responses are also copied into cache only when change numbers still match.
- Request finalization is critical: many paths hold file-node resources or captured security/token handles across user-mode transactions.
