## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeComparatorWrapperTest.java

### Purpose

`NativeComparatorWrapperTest` verifies that a Java wrapper around a native comparator can be installed in `Options` and used to order keys across DB reopen.

### Important APIs, Types, And Functions

It uses `NativeComparatorWrapper`, `Options.setComparator`, `RocksDB.put`, `RocksIterator`, and a nested `NativeStringComparatorWrapper` whose `initializeNative` calls a native `newStringComparator()` method.

### Control Flow

The test generates 1,000 unique random lowercase keys, writes each to a DB configured with the native string comparator, sorts the Java copy of keys with `Comparator.naturalOrder`, reopens the DB with the same options, iterates from first to last, and compares iterator keys with the sorted Java array.

### State And Persistence Behavior

Keys are persisted to the temporary DB. The test specifically checks comparator metadata and ordering survive close/reopen when the same comparator wrapper is supplied.

### Dependencies And Integration Points

This integrates JNI comparator initialization, native comparator ownership under `Options`, iterator ordering, Java random key generation, and RocksDB library loading through a static `RocksDB.loadLibrary`.

### Risks And Edge Cases

- Duplicate random keys are skipped by checking `db.get`; the loop decrements to maintain exactly 1,000 stored keys.
- Comparator wrapper native lifetime must remain valid while options and reopened DB handles use it.
- Natural Java string order is assumed to match the native comparator created by `newStringComparator`.

### Test Signals

The iterator must produce exactly the Java-sorted key sequence. Static research only; no test command was run.
