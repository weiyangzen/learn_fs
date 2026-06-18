# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWalFilter.java

- **Purpose:** Base Java callback bridge for RocksDB write-ahead-log filtering during WAL replay/processing.
- **Important APIs/types/functions:** Extends `RocksCallbackObject` and implements `WalFilter`. `initializeNative()` calls `createNewWalFilter()`. Private `logRecordFoundProxy(...)` creates Java `WriteBatch` wrappers around borrowed native batch handles and packs `LogRecordFoundResult` into a short.
- **Control flow:** Native code calls `logRecordFoundProxy` with log metadata and two batch handles. The method delegates to user `logRecordFound(...)` and encodes the returned WAL processing option in the high byte plus `batchChanged` in the low bit.
- **State and persistence behavior:** The filter can affect WAL replay behavior and optionally modify replacement write batches; durable consequences are in recovered database state, not Java fields.
- **Dependencies:** Depends on `RocksCallbackObject`, `WalFilter`, `WriteBatch`, and native callback allocation.
- **Integration points:** Used by database open/recovery paths that support application filtering or rewriting of WAL records.
- **Risks:** `WriteBatch` wrappers are created for handles the filter does not own; retaining or closing them incorrectly can corrupt native recovery. Null `LogRecordFoundResult` is not guarded. Bit packing must stay compatible with native enum values.
- **Test signals:** WAL replay with keep/skip/stop options, `batchChanged` propagation, replacement batch mutation, borrowed-handle lifecycle, and native decode of packed results.
