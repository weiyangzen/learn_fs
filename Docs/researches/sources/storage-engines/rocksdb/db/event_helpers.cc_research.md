# sources/storage-engines/rocksdb/db/event_helpers.cc

## Purpose

This file implements RocksDB event-helper routines that centralize listener notification and event logging for table-file creation/deletion, blob-file creation/deletion, background errors, and error-recovery completion. It also wires `EventListener::CreateFromString()` through the customizable object loader.

The implementation is pure glue: it packages internal DB event data into listener-facing structs, emits JSON records through `EventLogger`, and carefully releases the DB mutex around callbacks that may call back into user code.

## Important APIs, Types, and Functions

- `EventListener::CreateFromString()` calls `LoadSharedObject<EventListener>()`, enabling listener creation from the RocksDB customization registry.
- `SafeDivide()` returns zero on a zero denominator and is used for average key/value sizes in table-property JSON.
- `EventHelpers::AppendCurrentTime()` writes `time_micros` based on `std::chrono::system_clock`.
- `NotifyTableFileCreationStarted()` builds `TableFileCreationBriefInfo` and invokes `OnTableFileCreationStarted()` on all listeners.
- `NotifyOnBackgroundError()` asserts the DB mutex is held, unlocks it, invokes `OnBackgroundError()`, permits unchecked status handling, optionally invokes `OnErrorRecoveryBegin()`, and relocks the mutex.
- `LogAndNotifyTableFileCreationFinished()` logs rich table-file creation JSON and sends `TableFileCreationInfo` to `OnTableFileCreated()`.
- `LogAndNotifyTableFileDeletion()` logs deletion JSON and sends `TableFileDeletionInfo`.
- `NotifyOnErrorRecoveryEnd()` copies old/new background errors under mutex, unlocks, emits legacy and newer recovery-end callbacks, and relocks.
- Blob helpers mirror the table-file flow for `BlobFileCreationBriefInfo`, `BlobFileCreationInfo`, and `BlobFileDeletionInfo`.

## Control Flow and State Behavior

Every helper has a fast exit when both logging and listener notification are unnecessary. If no logger/listener consumes a `Status`, the code calls `PermitUncheckedError()` so RocksDB's unchecked-status diagnostics do not fire for intentionally ignored values.

Logging paths allocate a local `JSONWriter`, append the timestamp, then serialize event-specific fields before calling `event_logger->Log()`. Table creation logging includes file descriptor metadata, checksum information, sequence-number bounds, blob-file linkage, full `TableProperties`, user-readable properties, and a decoded human-readable `seqno_to_time_mapping` when possible.

Listener paths fill concrete listener info structs after logging. Status objects copied into those structs are also permitted as unchecked after callbacks return. Background-error and recovery-end notification paths intentionally release `db_mutex` while invoking arbitrary listener code; recovery-end copies statuses first to avoid races while the lock is released.

## Persistence and External Effects

This file does not persist data directly. Its external effects are event-log records and calls into user-supplied `EventListener` implementations. Event logs become operational observability data for table/blob creation and deletion. Listener callbacks can mutate control state: notably `NotifyOnBackgroundError()` passes a mutable `Status* bg_error` and `bool* auto_recovery`, allowing a listener to override error severity/status or veto automatic recovery.

## Dependencies and Integration Points

The implementation depends on `db/event_helpers.h`, `rocksdb/listener.h`, `logging/event_logger.h`, `rocksdb/convenience.h`, `rocksdb/utilities/customizable_util.h`, table properties, file descriptors, and mutex instrumentation. `TEST_SYNC_POINT` calls in `NotifyOnErrorRecoveryEnd()` are consumed by tests such as `error_handler_fs_test.cc` to force races while the DB mutex is unlocked.

Production callers include flush/table-build, compaction, blob-file, manifest/error-handler, and file-deletion paths that need consistent listener and JSON behavior.

## Risks and Maintenance Notes

The mutex-unlock sections are correctness-sensitive because listener code is arbitrary. Any new callback added here must avoid using references to mutable DB state after unlocking unless it first makes stable copies.

JSON field names are operationally visible. There is a likely field swap in the creation-time block: `"oldest_key_time"` is populated from `newest_key_time` and `"newest_key_time"` from `oldest_key_time`; changing it may affect log consumers but leaving it may mislead diagnostics.

`NotifyOnBackgroundError()` invokes `OnErrorRecoveryBegin()` only if `*auto_recovery` is still true after `OnBackgroundError()`, so listener ordering can affect recovery policy. Blob creation logs do not hex-escape `file_checksum` unlike table creation, which may be intentional but is a consistency risk for binary checksum strings.

## Test Signals

Direct signals are the DB listener and error-handling tests. `error_handler_fs_test.cc` validates background error mutation, auto-recovery veto, recovery-end callbacks, and mutex-release race handling. Event log correctness is indirectly covered by table/blob event tests elsewhere; useful assertions include JSON field presence, status propagation, and callbacks firing exactly once per event.
