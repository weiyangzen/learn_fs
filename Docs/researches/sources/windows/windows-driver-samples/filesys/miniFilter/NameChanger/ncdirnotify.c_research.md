# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirnotify.c

## Scope

This file implements directory change notification handling for the Windows Driver Samples NameChanger minifilter. The driver exposes a user-visible mapping path while backing it with a separate real path, so directory notifications need to hide, translate, split, merge, buffer, cancel, and reissue notifications depending on the relationship between the watched directory and the user/real mappings.

## APIs and Entry Points

- `NcPreNotifyDirectory` is the main pre-operation callback for `IRP_MJ_DIRECTORY_CONTROL / IRP_MN_NOTIFY_CHANGE_DIRECTORY`.
- `NcPostNotifyDirectory` is the post-operation callback that defers pageable work to `NcPostNotifyDirectorySafe` with `FltDoCompletionProcessingWhenSafe`.
- `NcPostNotifyDirectoryReal` is the shared completion engine for user requests and internally generated subrequests.
- `NcDirNotifyTranslateBuffers` rewrites `FILE_NOTIFY_INFORMATION` chains from filesystem-visible names to user-visible names and suppresses entries that should not be exposed.
- `NcBuildSubNotifyRequest` and `NcCleanupSubNotifyRequest` allocate, initialize, and tear down internal notify callback data.
- `NcAllocateNotifyRequestContext` and `NcFreeNotifyRequestContext` manage per-subrequest context references.
- `NcGetDestinationNotifyBuffer` maps or validates notify output buffers for MDL, system-buffered, and direct user-buffer cases.
- `NcNotifyCancelCallback` handles cancellation of a pended user notification.
- `NcNotifyAbort` is shared by cancellation and handle cleanup.
- `NcReissueNotifyRequestWorkerRoutine` reissues an internal notify request from passive-level work item context.
- `NcCloseHandleWorkerRoutine` closes the real mapping parent handle from a work item when inline close is not appropriate.
- `NcStreamHandleContextNotCreate`, `NcStreamHandleContextNotCleanup`, and `NcStreamHandleContextNotClose` initialize and tear down the directory notification portion of a stream-handle context.

## Control Flow

`NcPreNotifyDirectory` classifies the watched path against both mappings with `NcComparePath`:

- If the watched directory is inside either mapping, notifications are already relative to that handle and the request passes through.
- If the watched directory is unrelated to both mappings, the request passes through.
- If it is a non-recursive watch on an ancestor that is not a direct parent, the request passes through.
- If the watch is an ancestor or parent of the real mapping but not the user mapping, the context enters `Filter` mode. The user request is pended, a shadow request is sent to the filesystem, and completions suppress entries under the hidden real mapping.
- If the watch covers a common ancestor or common parent of both mappings, the context enters `Munge` mode. The user request goes to the filesystem with a post callback, and returned real-mapping paths are translated to user-mapping paths.
- If the watch covers the user mapping side but not the real mapping side, the context enters `Merge` mode. The driver opens the real mapping parent, issues one request on the user's handle and one on the real parent handle, then completes the user's pended request when either side produces visible data.

`NcPostNotifyDirectoryReal` processes completions under the stream-handle context lock. It handles cleanup and cancel states first, copies nonvolatile notification data into pool, translates entries through `NcDirNotifyTranslateBuffers`, completes the user request, buffers a second merge completion if no user request is waiting, or records `STATUS_NOTIFY_ENUM_DIR` for the next user call when output was insufficient.

If translation removes every entry from a `Filter` or `Merge` subrequest, the file reuses and reissues that subrequest on a passive-level work item instead of completing the user request with an empty success.

## State and Data Flow

The file depends heavily on `NC_DIR_NOT_CONTEXT` stored in the stream-handle context. Important fields are:

- `Mode`: `Uninitialized`, `Filter`, `Munge`, or `Merge`.
- `CancelSeen` and `CleanupSeen`: prevent stale completions from returning data after cancellation or cleanup.
- `InsufficientBufferSeen`: records that the next caller should receive `STATUS_NOTIFY_ENUM_DIR`.
- `UserRequestName` and `MappingParentName`: saved opened names used to reconstruct full paths from relative notification entries.
- `UserRequest`, `ShadowRequest`, and `MappingRequest`: the pended user request and up to two internal requests.
- `RealParentHandle`, `RealParentFileObject`, and `RealParentCloseWorkItem`: merge-mode access to the real mapping parent.
- `BufferToFree` and `BufferLength`: one held-over translated notification buffer for merge completions that arrive when no user request is pending.

`NcDirNotifyTranslateBuffers` consumes a source `FILE_NOTIFY_INFORMATION` chain, constructs full paths from `OpenedName + "\\" + FileName`, checks overlap with the real mapping, optionally constructs a user-mapping path with `NcConstructPath`, then emits relative names under `UserRequestName`. Output entries are aligned to 8 bytes and linked with `NextEntryOffset`.

## Dependencies

- Includes `nc.h` and uses the NameChanger mapping helpers, especially `NcComparePath`, `NcConstructPath`, `NcGetFileNameInformation`, `NcCreateFileHelper`, `NcSetCancelCompletion`, and `NcExceptionFilter`.
- Uses Filter Manager callback-data APIs: `FltAllocateCallbackData`, `FltFreeCallbackData`, `FltPerformAsynchronousIo`, `FltCompletePendedPreOperation`, `FltDoCompletionProcessingWhenSafe`, `FltReuseCallbackData`, `FltCancelIo`, `FltLockUserBuffer`, `FltClearCancelCompletion`, and context reference APIs.
- Uses MDL and buffer mapping APIs: `MmGetSystemAddressForMdlSafe`, `ProbeForWrite`, and optional `NcGetNewSystemBufferAddress`.
- Uses pool allocation tags `NC_TAG` and `NC_GENERATE_NAME_TAG`.
- Uses Windows notification structures and statuses: `FILE_NOTIFY_INFORMATION`, `STATUS_NOTIFY_CLEANUP`, `STATUS_NOTIFY_ENUM_DIR`, `STATUS_CANCELLED`, `STATUS_INVALID_USER_BUFFER`, and related NTSTATUS values.

## Risks and Edge Cases

- The code intentionally supports only one outstanding user notify request per handle; a second active user request asserts and fails with `STATUS_UNSUCCESSFUL`.
- Notification buffers are treated as untrusted even after copying because they may originate from user-mode memory. The translation helper uses safe arithmetic, explicit bounds checks, and exception handling.
- Zero-length buffers and buffers too small for translated output result in `STATUS_NOTIFY_ENUM_DIR`, requiring callers to rescan.
- Merge mode stores only one deferred buffer. The comments acknowledge cancellation races where multiple completions can arrive, and cancellation is allowed to discard buffered data.
- Cleanup and cancellation are lock-sensitive. `NcNotifyAbort` may drop the stream-handle lock before completing user requests, cancelling child requests, or queueing handle-close work.
- `Munge` mode relies on post-operation processing of the user's original request. During filter draining, the code frees the request context but cannot return `STATUS_NOTIFY_ENUM_DIR` because it no longer owns the request.
- Internal reissue depends on work item allocation and passive-level execution; allocation failure turns into request failure.
- The code has compatibility branches for systems with and without `FltGetNewSystemBufferAddress`; incorrect assumptions about buffer ownership would be dangerous in kernel mode.

## Research Notes

This file is the notification counterpart to NameChanger's create/name mapping logic. It preserves the illusion that the user mapping is the real namespace by either hiding real-path events, rewriting common-ancestor events, or merging notifications from the user's opened path and the real mapping parent.
