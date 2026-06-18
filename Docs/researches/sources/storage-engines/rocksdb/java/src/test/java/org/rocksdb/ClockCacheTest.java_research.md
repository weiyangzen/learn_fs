# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ClockCacheTest.java

## Purpose

Smoke-tests construction and native ownership of the Java `ClockCache` wrapper.

## Important APIs, control flow, and dependencies

The test creates a `ClockCache` with capacity, shard bits, and strict capacity limit in a try-with-resources block. It depends on `RocksNativeLibraryResource` and the `Cache` base type.

## State, persistence, risks, and test signals

No DB state is persisted. The important state is native cache allocation and release through `close()`. The risk is JNI constructor mismatch or leaking native cache handles. Passing construction and disposal without exception is the test signal.
