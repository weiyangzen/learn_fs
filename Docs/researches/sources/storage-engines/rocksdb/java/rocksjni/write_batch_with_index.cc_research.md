# sources/storage-engines/rocksdb/java/rocksjni/write_batch_with_index.cc

## Purpose
This file bridges Java `WriteBatchWithIndex` and `WBWIRocksIterator` to C++ `WriteBatchWithIndex` and `WBWIIterator`. It supports indexed batch mutation, batch reads, merged DB reads, iterator navigation, and write-entry extraction.

## Important APIs, Types, and Functions
Exports include constructors with default, overwrite-key, and comparator/reserved-bytes options; count, put, merge, delete, single delete, delete range, log data, clear, savepoint, max bytes, `getWriteBatch`, iterator creation, `getFromBatch`, `getFromBatchAndDB`, disposal, WBWI iterator navigation, seek variants, status, entry extraction, and unsupported refresh methods.

## Control Flow
Mutation methods mirror `write_batch.cc`, using `JniUtil` conversion helpers around C++ `WriteBatchWithIndex` methods. Constructors choose either bytewise comparator or a fallback comparator based on a Java comparator type byte. Read helpers build lambdas for `GetFromBatch` or `GetFromBatchAndDB` and call `JniUtil::v_op`. Iterator constructors allocate C++ iterators. Seek methods copy byte-array targets or use direct-buffer helpers. `entry1` reads `WBWIIterator::Entry`, allocates native `Slice` wrappers for key and optional value, and returns a three-element `long[]` of write type, key slice handle, and value slice handle.

## State and Persistence Behavior
The object stores an in-memory write batch plus an index for lookup and iteration. It can read through to a base DB, but persistence occurs only when the underlying write batch is later written. Iterator state advances independently. `getWriteBatch` exposes the underlying batch pointer to Java, and disposal deletes the `WriteBatchWithIndex`.

## Dependencies and Integration Points
It depends on `rocksdb/utilities/write_batch_with_index.h`, generated `WriteBatchWithIndex` and `WBWIRocksIterator` headers, comparator types, and RocksJNI portal utilities. It integrates with Java comparators, `DirectSlice`, `WriteBatch`, `DBOptions`, `ReadOptions`, `RocksDB`, and column-family handles.

## Risks and Edge Cases
The `putDirectJni` and `deleteDirectJni` implementations cast the handle to `WriteBatch*` even though the Java method name is for `WriteBatchWithIndex`; this is suspicious because it may bypass or corrupt the indexed batch object unless Java passes an underlying write batch handle. `getWriteBatch` has a TODO about ownership, making wrapper disposal semantics important. `entry1` returns heap-allocated `Slice` wrappers that Java must close via `DirectSlice`. Seek methods allocate arrays based on Java lengths and must handle exceptions. Refresh is explicitly unsupported and always throws.

## Test Signals
Tests should cover all mutation variants, comparator-backed construction, overwrite-key behavior, indexed lookup with and without DB fallback, iterator order, column-family iteration, direct and indirect seek variants, `entry1` slice cleanup, unsupported refresh exceptions, and ownership of `getWriteBatch`.
