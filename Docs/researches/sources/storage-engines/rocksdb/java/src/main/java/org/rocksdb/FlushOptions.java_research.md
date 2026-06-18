# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushOptions.java

Purpose: native options object for `RocksDB.flush` operations. APIs control whether flush waits for completion and whether the flush may immediately proceed even if it stalls writes.

Control flow loads the native library before allocation, asserts handle ownership in getters/setters, forwards to native methods, and disposes the native handle. State is native and consumed by flush calls; Java does not persist it. Dependencies include `RocksObject` and `RocksDB`.

Risks: `newFlushOptionsInance` contains a misspelling but is private; write-stall behavior can materially affect availability; assertions may be disabled. Tests should round-trip `waitForFlush` and `allowWriteStall`, exercise synchronous/asynchronous flush behavior, verify write-stall option semantics under load, and ensure disposal invalidates no in-flight operation.
