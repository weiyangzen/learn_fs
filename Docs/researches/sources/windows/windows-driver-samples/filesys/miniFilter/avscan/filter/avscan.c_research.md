# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.c

Main kernel minifilter implementation for the AV scan sample. It registers Filter Manager callbacks for create, cleanup, write, set-information, and file-system-control, owns driver initialization/unload, volume instance setup/teardown, scan dispatch, file-state cache synchronization, transaction outcome handling, and policy decisions about when to scan or skip a stream.

Key responsibilities:
- `DriverEntry` initializes `Globals`, scan-context list locking, registry-configured timeouts, Filter Manager registration, and three communication ports.
- `AvUnload` marks unloading, notifies the user-mode scanner, closes communication ports, unregisters the filter, and deletes global resources.
- `AvInstanceSetup` skips network file systems and hidden CSV NTFS volumes, creates an instance context, initializes an AVL file-state cache for NTFS/CSVFS/ReFS, and registers the instance for data scan.
- `AvPreCreate` filters out stack file objects, directories, rename target-directory opens, paging files, DASD opens, CSV downlevel opens, and prefetch opens; it synchronizes post-create processing.
- `AvPostCreate` creates or retrieves stream contexts, loads cached state by file ID, handles transaction context transitions, runs CSVFS revision checks, scans modified streams, and cancels infected opens with `STATUS_VIRUS_INFECTED`.
- `AvPreCleanup` scans modified non-transacted files before cleanup, updates CSVFS revision data after successful scans, and persists clean/infected state to the per-instance cache.
- `AvPreOperationCallback` marks stream state modified for writes, selected FSCTLs, EOF changes, and valid-data-length changes, while respecting transacted writer state.
- `AvPreFsControl` rejects TxF savepoint control and delegates other modifying FSCTLs to the generic pre-operation path.
- `AvKtmNotificationCallback`, `AvProcessPreviousTransaction`, and `AvProcessTransactionOutcome` maintain transaction-isolated `TxState` and propagate it to normal stream state only on commit.
- `AvScan` serializes scans per stream with `ScanSynchronizationEvent`, skips empty files, invokes either user-mode or kernel-mode scan, and handles cancellable waits.

Important data flow:
- A stream starts as `AvFileModified`; after a successful scan it becomes clean or infected.
- NTFS/CSVFS/ReFS file IDs allow volatile cache lookups through `AvLoadFileStateFromCache` and writes through `AvSyncCache`.
- Transacted writers use `TxState`; commit propagates transaction state, rollback discards it.
- CSVFS revision numbers can force rescans when another cluster node may have changed the file.
- User-mode scans are the normal path via `AvScanInUser`; kernel-mode scanning is supported but not the default in the create/cleanup paths.

Concurrency and lifecycle notes:
- `Globals.ScanCtxListLock` protects the global active scan list and unloading flag.
- Per-stream scanning is serialized with a nonpaged event held in the stream context.
- Transaction context lists are protected by per-transaction `ERESOURCE`.
- Instance teardown walks active scans for that instance, asks user mode to abort, and force-finalizes scans if abort messaging fails.
- The file-state cache is unbounded by design; comments explicitly warn production filters should cap it.

Dependencies:
- Internal: `avscan.h`, `context.h`, `scan.h`, `csvfs.h`, `utility.h`, `avlib.h`.
- Windows kernel APIs: Filter Manager, KTM/TxF, ECPs, `ERESOURCE`, generic AVL table, registry APIs, section data scan APIs.

Research notes:
- This is sample-quality AV logic, not a production policy engine. It chooses availability over strict blocking on timeout/failure, with comments noting this may allow a security gap.
- Alternate data streams are skipped deliberately.
- Encrypted backup/raw opens are skipped to avoid NTFS encryption-context assertions.
- Prefetch opens are tagged with stream-handle context and excluded from scan and write-modification tracking to avoid deadlocks.
