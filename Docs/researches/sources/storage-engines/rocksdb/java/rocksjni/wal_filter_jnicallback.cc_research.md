# sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.cc

## Purpose
This file implements the C++ `WalFilterJniCallback` that forwards RocksDB WAL filter calls into Java `AbstractWalFilter`.

## Important APIs, Types, and Functions
The constructor caches the Java filter name and method IDs for `columnFamilyLogNumberMap` and `logRecordFoundProxy`. It implements `ColumnFamilyLogNumberMap`, `LogRecordFound`, and `Name`.

## Control Flow
Construction calls Java `name()`, copies the string into `m_name`, and caches method IDs. `ColumnFamilyLogNumberMap` attaches to the JVM, converts C++ maps to Java hash maps, calls the Java callback, deletes local refs, describes exceptions, and releases the environment. `LogRecordFound` converts the log file name to Java, calls the Java proxy with log number and native write batch handles, decodes a packed short into a `WalProcessingOption` byte and `batch_changed` flag, then returns the converted C++ option.

## State and Persistence Behavior
The callback stores the immutable filter name and method IDs. During WAL replay it may influence recovery state by returning processing options and indicating whether a replacement write batch was produced. It does not itself persist data.

## Dependencies and Integration Points
It depends on conversion helpers, portal method lookups, `WalFilter`, `WriteBatch`, and Java `AbstractWalFilter`. It is constructed by `wal_filter.cc` and used by RocksDB WAL recovery.

## Risks and Edge Cases
If Java name or method lookup fails in the constructor, the object may be partially initialized. Exceptions inside callbacks are described to stderr and often degrade to `kCorruptedRecord`, which can affect recovery. The packed short contract between Java and C++ must keep high byte as processing option and low byte as `batch_changed`. `Name()` returns `m_name.get()`, so `m_name` must be set.

## Test Signals
Tests should verify name caching, map conversion for column-family/log-number metadata, all `WalProcessingOption` values, `batch_changed` propagation with replacement batches, and callback exception behavior during recovery.
