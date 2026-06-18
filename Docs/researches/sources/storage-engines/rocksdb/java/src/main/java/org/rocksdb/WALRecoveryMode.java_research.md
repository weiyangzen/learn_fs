# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WALRecoveryMode.java

## Purpose
`WALRecoveryMode` models RocksDB write-ahead-log recovery strictness. It controls how recovery handles corrupted or incomplete WAL records.

## Important APIs and Types
Values are `TolerateCorruptedTailRecords`, `AbsoluteConsistency`, `PointInTimeRecovery`, and `SkipAnyCorruptedRecords`, each with a native byte. `getValue()` and `getWALRecoveryMode(byte)` perform JNI conversion.

## Control Flow, State, and Persistence
The enum is immutable. Recovery behavior is external: choices range from legacy tolerance of trailing incomplete records to strict clean-shutdown recovery, point-in-time stop on inconsistency, or salvage mode that skips corruption.

## Dependencies and Integration Points
This enum is consumed by DB option bindings that configure WAL recovery. It must remain aligned with native constants and persisted WAL semantics.

## Risks and Test Signals
Misconfiguration changes durability and data-loss tradeoffs. Unknown native bytes throw `IllegalArgumentException`. Backup tests in this subset rely on WAL-backed DB behavior, but they do not exercise explicit recovery modes.
