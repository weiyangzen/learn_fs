# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.c

## Purpose

Implements a transaction-aware minifilter sample that tracks whether file contents have become dirty. It distinguishes normal dirty state from transaction-local dirty state and propagates transaction changes only on KTM commit.

## Public And Internal APIs

- Driver/instance lifecycle: `DriverEntry()`, `CgUnload()`, `CgInstanceSetup()`, `CgInstanceQueryTeardown()`, `CgInstanceTeardownStart()`, `CgInstanceTeardownComplete()`.
- Operation callbacks: `CgPreCreate()`, `CgPostCreate()`, `CgPreClose()`, `CgPreOperationCallback()`, `CgPreFsControl()`.
- KTM callback: `CgKtmNotificationCallback()`.
- Dirty/transaction helpers: `CgOperationsNeedDirty()`, `CgQueryTransactionOutcome()`, `CgProcessPreviousTransaction()`, `CgProcessTransactionOutcome()`, inline `CgPropagateDirty()`.

## Registration

- Registers callbacks for:
  - `IRP_MJ_CREATE`: pre and post.
  - `IRP_MJ_CLOSE`: pre.
  - `IRP_MJ_WRITE`: pre dirty tracking.
  - `IRP_MJ_SET_INFORMATION`: pre dirty tracking.
  - `IRP_MJ_FILE_SYSTEM_CONTROL`: pre savepoint handling and dirty tracking.
- Uses context registration from `context.c`.
- Supplies `CgKtmNotificationCallback` as the transaction notification callback.

## Dirty Tracking Semantics

- `CgOperationsNeedDirty()` returns true for content-affecting operations:
  - All writes.
  - FSCTLs `FSCTL_OFFLOAD_WRITE`, `FSCTL_WRITE_RAW_ENCRYPTED`, `FSCTL_SET_ZERO_DATA`.
  - Set-information classes `FileEndOfFileInformation` and `FileValidDataLengthInformation`.
- `CgPreOperationCallback()` obtains the file context; if the file has an active transaction context, it sets `TxDirty`, otherwise it sets `Dirty`.
- `CgPropagateDirty()` ORs `TxDirty` into `Dirty` only if the transaction committed, then clears `TxDirty` regardless of outcome.

## Transaction Flow

- `CgPostCreate()` ignores failed/reparse creates, finds or creates the file context, and if desired access includes write/delete/security-changing rights, calls `CgProcessPreviousTransaction()`.
- `CgProcessPreviousTransaction()` finds or creates a transaction context when `FltObjects->Transaction` is non-null, enlists it for `TRANSACTION_NOTIFY_COMMIT_FINALIZE | TRANSACTION_NOTIFY_ROLLBACK`, then atomically swaps `FileContext->TxContext`.
- When moving a file context between transactions, it queries the old transaction outcome, removes the file from the old transaction list, propagates dirty state if appropriate, updates references, and inserts into the new transaction list if still active.
- `CgProcessTransactionOutcome()` drains the transaction context’s file-context list under its mutex, atomically clears matching `TxContext` pointers, propagates dirty state for commit, releases transaction/file references, marks the list drained, and prints dirty file IDs in debug output.
- `CgKtmNotificationCallback()` maps commit-finalize to `TransactionOutcomeCommitted`; rollback maps to `TransactionOutcomeAborted`.

## Other Control Flow

- `CgPreCreate()` returns `FLT_PREOP_SYNCHRONIZE` so `CgPostCreate()` runs at a safe IRQL for context/resource work.
- `CgPreFsControl()` explicitly fails `FSCTL_TXFS_SAVEPOINT_INFORMATION` with `STATUS_NOT_SUPPORTED`, because the sample does not support savepoints.
- `CgPreClose()` reports non-transacted dirty files on close.
- Instance setup/query teardown always succeeds; teardown callbacks only log.

## Dependencies

- Filter Manager: `FltRegisterFilter`, `FltStartFiltering`, `FltUnregisterFilter`, file and transaction contexts, transaction enlistment.
- KTM/transaction APIs: `FltEnlistInTransaction`, `ZwQueryInformationTransaction`, `ObOpenObjectByPointer`, `TmTransactionObjectType`.
- Context helpers from `context.c`: `CgFindOrCreateFileContext()`, `CgFindOrCreateTransactionContext()`.
- List and mutex helpers from `utility.h`.

## Risks And Invariants

- Transaction context replacement uses `InterlockedExchangePointer()` and `InterlockedCompareExchangePointer()` to coordinate with asynchronous KTM notifications.
- File contexts linked into transaction lists hold an extra file-context reference; the reference is released when the list entry is removed.
- Transaction contexts referenced by file contexts hold a separate context reference; it must be released when `TxContext` is cleared/replaced.
- KTM notifications can arrive out of order; committed dirty propagation uses OR assignment to avoid clearing existing dirty state.
- Savepoints are not modeled; the sample rejects them rather than attempting partial rollback tracking.
- The code assumes TxF semantics that only one transacted writer exists for a file at a time.
