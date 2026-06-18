# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationType.java research

## Purpose

`OperationType` maps high-level native thread operation bytes to Java constants for RocksDB thread status reporting.

## Important APIs and types

Constants are `OP_UNKNOWN`, `OP_COMPACTION`, `OP_FLUSH`, and `OP_DBOPEN`. `getValue()` returns the byte. Package-private `fromValue(byte)` performs byte decoding and throws `IllegalArgumentException` for unknown values.

## Control flow

Thread-status JNI constructs Java status objects by decoding native operation bytes. Java code then exposes operation type to callers.

## State and persistence behavior

The enum is immutable and reports transient runtime state only. It does not affect DB files or native operation scheduling.

## Dependencies and integration points

It integrates with thread tracking and status APIs, and must remain byte-compatible with the native operation type enum.

## Risks and test signals

Tests should verify byte mappings, invalid-byte rejection, and status reporting under controlled DB open, flush, and compaction activity.
