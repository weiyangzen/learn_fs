# sources/storage-engines/rocksdb/java/rocksjni/wal_filter.cc

## Purpose
This file constructs native WAL filter callback objects for Java `AbstractWalFilter` implementations.

## Important APIs, Types, and Functions
It exports `createNewWalFilter`, which allocates `WalFilterJniCallback` with the Java callback object and returns its native pointer.

## Control Flow
Java calls the native constructor hook. JNI receives the Java filter object, creates the C++ callback adapter, and returns the pointer with `GET_CPLUSPLUS_POINTER`. Disposal is handled by the Java callback object hierarchy and related native callback infrastructure, not in this file.

## State and Persistence Behavior
The file only creates callback state. The callback is later used during WAL recovery to observe and optionally modify WAL processing, but no persistence is done at construction time.

## Dependencies and Integration Points
It depends on the generated `AbstractWalFilter` JNI header, pointer conversion helpers, and `wal_filter_jnicallback.h`. It integrates with RocksDB options that accept a WAL filter.

## Risks and Edge Cases
Allocation failures are not explicitly handled. Correct lifetime depends on Java owning and disposing the callback consistently with RocksDB options and database lifetime. The Java object must remain valid while RocksDB may call into the filter.

## Test Signals
Tests should instantiate a Java WAL filter, open a DB with it, force WAL recovery, and verify that the callback methods are invoked and that native callback disposal occurs after DB shutdown.
