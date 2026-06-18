# File Research: sources/windows/winfsp/src/sys/dirctl.c

Purpose:
Implements WinFsp directory-control IRP handling for filesystem volume devices. It covers `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`, bridging Windows directory query buffers to WinFsp user-mode transaction responses and FSRTL directory change notifications.

Major entry points and roles:
- `FspDirectoryControl` is the `IRP_MJ_DIRECTORY_CONTROL` dispatch routine. It routes only filesystem-volume device objects to `FspFsvolDirectoryControl`.
- `FspFsvolDirectoryControl` switches minor functions between query directory and notify-change-directory.
- `FspFsvolQueryDirectory` validates the file object, directory status, and optional filename pattern, then delegates to retryable query logic.
- `FspFsvolQueryDirectoryRetry` is the main query path. It handles restart/index/single-entry flags, probes or locks the output buffer, consults cached directory info, computes an appropriate user-mode query size, builds `FspFsctlTransactQueryDirectoryKind`, and posts the IRP to the WinFsp I/O queue when kernel cache data is insufficient.
- `FspFsvolDirectoryControlPrepare` allocates a per-process shared buffer via `FspProcessBufferAcquire` and publishes its user-mode address in the request.
- `FspFsvolDirectoryControlComplete` consumes user-mode responses, optionally stores cacheable `FSP_FSCTL_DIR_INFO` buffers in the file node meta cache, copies results into the caller buffer, and reposts to user mode when a response contains no matching entries but scanning should continue.
- `FspFsvolNotifyChangeDirectory` registers change-notification IRPs with WinFsp/FSRTL notification state and hooks completion so the driver can release its device reference after FSRTL completes the IRP.

Directory copying behavior:
- `FspFsvolQueryDirectoryCopy` converts WinFsp `FSP_FSCTL_DIR_INFO` records into Windows `FILE_DIRECTORY_INFORMATION`, `FILE_FULL_DIR_INFORMATION`, `FILE_ID_FULL_DIR_INFORMATION`, `FILE_NAMES_INFORMATION`, `FILE_BOTH_DIR_INFORMATION`, or `FILE_ID_BOTH_DIR_INFORMATION`.
- It applies wildcard matching through `FspFileNameInExpression` unless the cached match-all sentinel is used.
- It supports two marker modes: filename marker strings and `DirectoryMarkerAsNextOffset`, where the marker is a `UINT64` next offset supplied by the filesystem.
- Output records are aligned with `FSP_FSCTL_ALIGN_UP(..., sizeof(LONGLONG))`, and previous records receive `NextEntryOffset`.
- It distinguishes `STATUS_BUFFER_TOO_SMALL` from `STATUS_BUFFER_OVERFLOW`: too small means even the fixed header cannot fit, while overflow may copy a truncated first filename.
- EA-size fields are populated only for EA-capable volumes. For reparse points, the EA-size field is used to carry the reparse tag, matching Windows/NTFS behavior noted in the source comments.

Caching and scan state:
- `FspFsvolQueryDirectoryCopyCache` uses `FileDesc->DirInfoCacheHint` and `FileDesc->DirectoryMarker` to resume scanning cached directory info. It resets hints when cache state changes or restart/index flags force a reset.
- `FspFsvolQueryDirectoryCopyInPlace` performs the same conversion directly from the current response buffer when caching is not used.
- `DirectoryHasSuchFile` converts a first `STATUS_NO_MORE_FILES` into `STATUS_NO_SUCH_FILE` when no matching entry has ever been returned for the current pattern.
- Query-size selection is tuned by volume parameters: directory info cache timeout, `PassQueryDirectoryPattern`, `PassQueryDirectoryFileName`, max component length, and whether the pattern is a full wildcard, partial wildcard, or literal file name.

Concurrency and lifetime:
- Query handling acquires `FSP_FILE_NODE` resources in full or main mode depending on whether it may need user-mode traffic. It uses owner handoff (`FspFileNodeSetOwner`, `FspFileNodeReleaseOwner`) across asynchronous requests.
- User-mode process buffers are released in `FspFsvolQueryDirectoryRequestFini`, attaching back to the original process when needed before `FspProcessBufferRelease`.
- Notify-change completion cannot run pageable cleanup directly, so `FspFsvolNotifyChangeDirectoryCompletion` queues `FspFsvolNotifyChangeDirectoryCompletionWork`, which dereferences the fsvol device and frees the completion context.

Dependencies:
- Declared shared types and helpers come from `sys/driver.h`.
- Uses WinFsp file-node/file-desc APIs for directory markers, meta-cache references, owner transfer, and cache invalidation state.
- Uses Windows kernel APIs and FSRTL concepts: IRPs, MDLs, `MmGetSystemAddressForMdlSafe`, `FsRtlDoesNameContainWildCards`, notify packages, `IoGetTopLevelIrp`, and work items.
- User-mode contract depends on `FSP_FSCTL_TRANSACT_REQ/RSP`, especially `Req.QueryDirectory` and `FSP_FSCTL_DIR_INFO`.

Research notes:
- The most important invariants are buffer bounds, aligned record traversal, and synchronized file-node owner release across retry/completion paths.
- Query-directory cache correctness depends on file-node directory change numbers and `FileDesc` marker/hint state.
- Notify-change deliberately clears `TopLevelIrp` because FSRTL may complete the IRP immediately before normal completion handling can run.
