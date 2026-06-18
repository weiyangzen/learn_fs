# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionPriorityTest.java

## Purpose

Validates Java enum mapping for `CompactionPriority`.

## Important APIs, control flow, and dependencies

The test calls `CompactionPriority.getCompactionPriority` with a valid enum byte and `valueOf` with a symbolic name, plus an invalid byte negative case.

## State, persistence, risks, and test signals

No native DB state is touched. The risk is byte-value drift between Java and C++ enum definitions. Signals are correct enum identity for valid inputs and `IllegalArgumentException` for invalid byte values.
