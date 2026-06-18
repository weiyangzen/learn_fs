# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionStopStyleTest.java

## Purpose

Validates Java enum mapping for universal compaction stop style.

## Important APIs, control flow, and dependencies

The test covers `CompactionStopStyle.getCompactionStopStyle`, `valueOf`, and invalid byte handling.

## State, persistence, risks, and test signals

No DB state is persisted. The risk is Java/C++ enum byte mismatch. Signals are expected enum identity for valid mappings and `IllegalArgumentException` for invalid values.
