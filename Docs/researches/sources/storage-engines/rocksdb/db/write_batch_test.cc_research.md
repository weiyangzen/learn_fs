# sources/storage-engines/rocksdb/db/write_batch_test.cc

Purpose: This unit-test file validates the `WriteBatch` serialized format, mutation APIs, handler iteration, memtable insertion semantics, column-family records, savepoints, wide-column entities, large-size boundaries, timestamp handling, and transaction marker callbacks.

Important APIs/types/functions: `PrintContents` inserts a batch into a temporary memtable and renders internal keys. `TestHandler` records callback events for all major tags. `ReplayUntilCountHandler` exercises `Continue()` while buffering prepared batches. `ColumnFamilyHandleImplDummy` supplies test CF IDs/comparators. `TimestampChecker` verifies trailing user-key timestamps.

Control flow: Tests build batches through public and internal APIs, set sequences, iterate through handlers, insert into memtables, and compare deterministic rendered strings. Append tests validate empty, non-empty, and WAL-termination append behavior. Prepared transaction tests use a leading noop rewritten by `MarkEndPrepare`. Continuation tests stop mid-batch and inside committed prepared replay. Column-family tests verify CF-tagged operations and `WriteBatchWithIndex` ordering. Timestamp tests create CFs with and without timestamp comparators, then update in-place.

State and persistence behavior: The tests inspect serialized batch effects through memtable state and handler callbacks. They validate count increments, sequence assignment, savepoint rollback restoring bytes/count/flags, memory limit rollback, `Release()` ownership transfer, WAL-only termination truncation, and preservation of serialized V2 wide-column entities without deserialize/re-serialize loss.

Dependencies and integration points: The file depends on blob indexes, column-family internals, DB test utilities, memtables, wide-column serialization/helper code, `WriteBatchInternal`, comparators, environments, write-batch-with-index, write buffer manager, and test utilities.

Risks: Some stress tests are disabled due to very high memory requirements. `PrintContents` is a test-only approximation of insertion behavior using a temporary default-CF memtable; full DB write/recovery behavior is covered elsewhere. String-order expectations depend on memtable internal ordering and sequence ordering.

Test signals: Coverage is broad for basic operations, corruption, append, log data, unsupported handler defaults, merge-operator requirements, gathered slices, attribute groups, serialized V2 entity rebuilding, CF-specific records, savepoints, memory limits, timestamp sanity/update, and commit-with-timestamp markers.
