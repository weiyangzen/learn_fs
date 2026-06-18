# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationStage.java research

## Purpose

`OperationStage` maps native thread-operation stage bytes to Java constants for RocksDB thread status reporting. It identifies fine-grained phases inside flush and compaction work.

## Important APIs and types

Constants include unknown, flush run/write-L0, compaction prepare/run/process/install/sync, memtable pick, rollback, and install-flush-results stages. `getValue()` returns the internal byte. Package-private `fromValue(byte)` decodes native bytes and throws on unknown values.

## Control flow

Native status code passes a byte into Java; Java calls `fromValue()` while constructing thread status objects. Unknown stage bytes produce an `IllegalArgumentException`.

## State and persistence behavior

The enum has only immutable byte values. It reports live runtime state and has no persistence behavior.

## Dependencies and integration points

It integrates with thread-status APIs and native operation-stage enums. Package-private access keeps it within the binding layer.

## Risks and test signals

Native enum drift is the main risk. Tests should decode every native stage, reject invalid bytes, and verify thread tracking reports expected stages during flush or compaction workloads.
