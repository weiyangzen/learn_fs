# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SnapshotTest.java

## Purpose

This suite validates Java snapshot handling: acquiring snapshots, binding them into `ReadOptions`, reading historical values, retrieving a snapshot from read options, releasing snapshots, and iterating with snapshots on default and explicit column-family APIs.

## Important APIs and types

The tests use `RocksDB.getSnapshot`, `releaseSnapshot`, `Snapshot.getSequenceNumber`, `ReadOptions.setSnapshot`, `ReadOptions.snapshot`, and `RocksIterator`.

## Control flow

The primary test writes a key, takes a snapshot, reads through normal and snapshot read paths, writes new keys/values, then verifies snapshot reads still see the previous version and miss later keys. Iterator tests compare current iterators with snapshot-bound iterators after a second key is inserted.

## State and persistence behavior

Snapshots represent native sequence-number state, not independent persisted files. The file tests consistent historical reads while later memtable/WAL updates occur. It also calls `releaseSnapshot` explicitly while using try-with-resources, making snapshot ownership behavior important.

## Dependencies and integration points

The suite connects `Snapshot`, `ReadOptions`, `RocksDB.get`, iterator creation, and column-family iterator overloads.

## Risks and test signals

Risks include using a moving latest view despite a snapshot, mishandling snapshot wrapper ownership, or returning a different native snapshot from `ReadOptions.snapshot()`. Signals are exact old/new value checks, null checks for post-snapshot keys, and iterator key sequences.
