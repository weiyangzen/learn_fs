## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ReadOnlyTest.java

### Purpose

`ReadOnlyTest` verifies read-only RocksDB open modes, CF selection, mutation rejection, write-batch rejection, and WAL-file existence protection.

### Important APIs, Types, And Functions

It uses `RocksDB.openReadOnly` overloads, `RocksDB.open`, `DBOptions`, `Options`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteBatch`, `WriteOptions`, `put`, `delete`, `write`, and `Files.write`.

### Control Flow

The main test writes data in read-write mode, reopens read-only and reads it, then creates extra CFs, writes data to `new_cf2`, and checks that read-only opening with only default cannot see it while opening with `new_cf2` can. Mutation tests open read-only and expect `RocksDBException` from plain/CF `put`, plain/CF `delete`, and write-batch writes. The WAL test creates a fake `.log` file and opens read-only with `errorIfWalFileExists=true`, expecting failure.

### State And Persistence Behavior

Temporary DB state persists across read-write close and read-only reopen. Read-only handles must not mutate DB files. The WAL existence check protects users from opening a DB read-only when unapplied WALs might exist.

### Dependencies And Integration Points

This integrates read-only DB open paths, CF descriptor lists, write APIs, write batch APIs, filesystem WAL checks, and exception propagation.

### Risks And Edge Cases

- Read-only CF descriptors control visibility; missing CFs should not be accidentally read through default handles.
- Mutating APIs must fail even though Java exposes them on the `RocksDB` type.
- The WAL test writes a synthetic `999999.log`, depending on RocksDB's WAL filename detection.

### Test Signals

Signals are successful reads for visible data, `null` for absent/wrong CF data, and expected `RocksDBException` for all read-only mutations and WAL conflict. Static research only; no test command was run.
