# sources/storage-engines/rocksdb/db/event_helpers.h

## Purpose

This header declares the `EventHelpers` utility class used by RocksDB DB internals to log event records and notify `EventListener` instances for table files, blob files, background errors, and recovery lifecycle events. It provides a narrow static API that keeps event packaging out of the individual DB code paths.

## Important APIs and Types

- `AppendCurrentTime(JSONWriter*)` appends the common timestamp field used by event-log records.
- `NotifyTableFileCreationStarted()` emits the lightweight pre-creation listener event with DB name, column family name, file path, job id, and `TableFileCreationReason`.
- `NotifyOnBackgroundError()` lets listeners observe and mutate a background error and auto-recovery decision while coordinating with `InstrumentedMutex`.
- `LogAndNotifyTableFileCreationFinished()` records and reports full SST creation metadata including `FileDescriptor`, oldest linked blob file number, `TableProperties`, status, and file checksum fields.
- `LogAndNotifyTableFileDeletion()` records and reports table deletion metadata.
- `NotifyOnErrorRecoveryEnd()` reports old and new background error state after recovery finishes.
- `NotifyBlobFileCreationStarted()`, `LogAndNotifyBlobFileCreationFinished()`, and `LogAndNotifyBlobFileDeletion()` are the blob-file analogs.
- Private `LogAndNotifyTableFileCreation()` is declared as an internal helper taking a `TableFileCreationInfo`, but it is not implemented or used in the paired `.cc` file in this snapshot.

## Control Flow and State Expectations

All methods are static and stateless. Callers pass listener vectors, logger pointers, DB/CF names, file identifiers, status objects, and mutex pointers. The contract implied by the header is that DB code remains owner of lifecycle state, while `EventHelpers` handles fan-out and observability.

The background-error and recovery-end APIs explicitly accept `InstrumentedMutex*`, signaling that implementations may unlock around callbacks. Callers must hold the mutex as required by the implementation and must tolerate listener-side changes to background error and auto-recovery flags.

## Dependencies and Integration Points

The header depends on `db/column_family.h`, `db/version_edit.h`, `logging/event_logger.h`, `rocksdb/listener.h`, and `rocksdb/table_properties.h`. It is included by DB implementation files that need listener notification without exposing all event-construction details inline.

It forms the public internal contract used by tests like `error_handler_fs_test.cc`, which relies on recovery begin/end and table-creation-started notifications to coordinate fault injection.

## Risks and Maintenance Notes

Because this header sits between core DB state machines and arbitrary listener code, signature changes have broad impact across flush, compaction, blob, deletion, and error-handler call sites. New fields should be added in a way that preserves listener ABI/API expectations.

The private `LogAndNotifyTableFileCreation()` declaration appears stale in this snapshot. If it remains unused, it can confuse maintainers looking for a shared implementation path. If revived, it should preserve the current logging and listener status-handling behavior in `event_helpers.cc`.

## Test Signals

Compile coverage is the primary header-level signal. Behavioral signals come from listener tests, event log tests, blob/table creation tests, and the background error recovery suite. Important assertions include that callbacks receive complete DB/CF/file/status metadata and that background-error callbacks can safely alter recovery decisions.
