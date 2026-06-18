# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/delete/delete.c

## Purpose
Self-contained delete-detection minifilter sample. It tracks streams that become deletion candidates through `FILE_DELETE_ON_CLOSE` or delete disposition changes, verifies deletion after cleanup, distinguishes file deletes from alternate data stream deletes, supports NTFS/ReFS differences, and defers transaction-related delete notifications until commit or rollback.

## Global Configuration
- `gFilterHandle`: registered filter handle.
- `gTraceFlags`: debug trace mask, defaulting to errors.
- Attaches only to writable NTFS or ReFS volumes.
- Registers callbacks for:
  - `IRP_MJ_CREATE`
  - `IRP_MJ_SET_INFORMATION`
  - `IRP_MJ_CLEANUP`
- Registers contexts:
  - `FLT_INSTANCE_CONTEXT`
  - `FLT_STREAM_CONTEXT`
  - `FLT_TRANSACTION_CONTEXT`

## Core Types
- `DF_FILE_REFERENCE`
  - Holds either a 64-bit NTFS file ID or 128-bit ReFS file ID.
  - `DfSizeofFileId` chooses the size based on whether upper 64 bits are zero.

- `DF_INSTANCE_CONTEXT`
  - Caches a volume GUID name.

- `DF_STREAM_CONTEXT`
  - Stores last opened-name information.
  - Stores file ID.
  - Tracks in-flight delete-disposition operations with `NumOps`.
  - Tracks notification state with `IsNotified`.
  - Tracks candidate state:
    - `SetDisp`
    - `DeleteOnClose`
    - `FileIdSet`

- `DF_TRANSACTION_CONTEXT`
  - Holds a list of pending delete notifications.
  - Uses a NonPagedPool `ERESOURCE` to protect the list.

- `DF_DELETE_NOTIFY`
  - List node for a pending delete notification inside a transaction.
  - References the stream context and records whether it was a file delete or stream delete.

## Initialization and Instance Handling
- `DriverEntry`
  - Opts into `NonPagedPoolNx`.
  - Registers and starts the minifilter.

- `DfUnload`
  - Unregisters the filter.

- `DfInstanceSetup`
  - Rejects read-only volumes.
  - Accepts writable `FLT_FSTYPE_NTFS` and `FLT_FSTYPE_REFS`.
  - Rejects other file systems.

- Teardown callbacks are trace-only and allow detach.

## Context Helpers
- `DfAllocateContext`
  - Allocates and initializes stream, transaction, or instance contexts.
  - Transaction contexts initialize `DeleteNotifyList` and allocate an `ERESOURCE`.

- `DfSetContext` / `DfGetContext`
  - Type-switching wrappers over Filter Manager context APIs.

- `DfGetOrSetContext`
  - Generic get-or-create-and-attach helper.
  - Handles already-attached context races.
  - Enlists in a transaction after setting a transaction context.

- Cleanup callbacks:
  - Stream cleanup releases `NameInfo`.
  - Transaction cleanup drains pending notifications, releases stream contexts, frees notify nodes, and deletes the resource.
  - Instance cleanup frees cached volume GUID name.

## Name and ID Helpers
- `DfGetFileNameInformation`
  - Gets opened file name, parses it, and atomically swaps it into stream context.

- `DfGetFileId`
  - Queries `FileInternalInformation`.
  - For ReFS-style invalid 64-bit ID, queries `FileIdInformation` to obtain 128-bit ID.
  - Uses `KeMemoryBarrier` before setting `FileIdSet`.

- `DfGetVolumeGuidName`
  - Gets or creates an instance context.
  - Lazily caches the volume GUID name with trailing backslash.
  - Uses `InterlockedCompareExchangePointer` to resolve concurrent cache population.

- `DfBuildFileIdString`
  - Builds a volume-GUID-plus-file-ID string for open-by-ID checks.

- `DfDetectDeleteByFileId`
  - Attempts `FltCreateFileEx2` with `FILE_OPEN_BY_FILE_ID`.
  - Uses transaction parameters when available.
  - Converts open-by-ID outcomes into deletion detection signals elsewhere.

## Delete Detection
- `DfPreCreateCallback`
  - If create has `FILE_DELETE_ON_CLOSE`, allocates a stream context and requests synchronized post-create callback.

- `DfPostCreateCallback`
  - On successful create, attaches or retrieves stream context.
  - Sets `DeleteOnClose` based on create options.

- `DfPreSetInfoCallback`
  - Handles `FileDispositionInformation` and `FileDispositionInformationEx`.
  - Gets or sets stream context.
  - Increments `NumOps` to detect racing delete-disposition changes.
  - If a race is detected, it deliberately does not request postop, leaving `NumOps` positive so cleanup will conservatively verify deletion.

- `DfPostSetInfoCallback`
  - Updates `SetDisp` or `DeleteOnClose` based on successful disposition operation.
  - Handles `FILE_DISPOSITION_INFORMATION_EX` distinction between `FILE_DISPOSITION_ON_CLOSE` and regular set-disposition behavior.
  - Decrements `NumOps`.

- `DfPreCleanupCallback`
  - Retrieves stream context if one exists.
  - Captures name information before cleanup completes.
  - Requests synchronized post-cleanup.

- `DfPostCleanupCallback`
  - Core deletion check.
  - If candidate state indicates possible deletion and no notification was sent, queries `FileStandardInformation`.
  - On `STATUS_FILE_DELETED`, calls `DfProcessDelete`.

- `DfIsFileDeleted`
  - Determines whether the whole file was deleted after a stream deletion.
  - Uses open-by-file-ID for transactions and ReFS.
  - Uses `FSCTL_GET_OBJECT_ID` as a cheaper NTFS non-transaction check.

- `DfProcessDelete`
  - Creates or gets transaction context if operation is transacted.
  - Calls `DfIsFileDeleted`.
  - Calls `DfNotifyDelete`.

## Transaction Notifications
- `DfNotifyDelete`
  - Prints immediate non-transaction delete messages.
  - For transaction deletes, adds a pending notification to the transaction context.

- `DfAddTransDeleteNotify`
  - Allocates a pending notification node.
  - References stream context.
  - Inserts it under transaction-context resource protection.

- `DfTransactionNotificationCallback`
  - Handles commit-finalize and rollback notifications.
  - Drains pending notifications.
  - On rollback, decrements `IsNotified`.
  - Logs final deleted or saved outcome.
  - Releases stream contexts and frees notification nodes.

## Research Notes
This sample is intentionally conservative. When delete-disposition operations race and final state cannot be known, it preserves candidate state and verifies deletion at cleanup. It also shows the extra complexity needed for:
- alternate data stream deletion versus whole-file deletion
- transactional NTFS-style delete semantics
- ReFS 128-bit file IDs
- safe context lifetime across transaction-deferred notifications
