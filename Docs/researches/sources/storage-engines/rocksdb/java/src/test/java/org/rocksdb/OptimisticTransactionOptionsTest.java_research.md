## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionOptionsTest.java

### Purpose

`OptimisticTransactionOptionsTest` checks the Java getter/setter binding for optimistic transaction snapshot behavior.

### Important APIs, Types, And Functions

The file uses `OptimisticTransactionOptions`, especially `setSetSnapshot` and `isSetSnapshot`, with native library loading through `RocksNativeLibraryResource`.

### Control Flow

The test constructs an options object, asserts the default snapshot flag, toggles it, and asserts the value changed.

### State And Persistence Behavior

Only in-memory native option state is involved. No DB or transaction is opened.

### Dependencies And Integration Points

This is a focused JNI binding test for options passed later to `OptimisticTransactionDB.beginTransaction`.

### Risks And Edge Cases

- Default value changes in native RocksDB would break the assertion.
- The test does not verify behavioral snapshot semantics, only option state.

### Test Signals

The snapshot flag must round-trip through Java and native getters/setters. Static research only; no test command was run.
