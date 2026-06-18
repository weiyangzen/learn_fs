# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteOptions.java

## Purpose
`WriteOptions` wraps native per-write configuration controlling durability, WAL use, missing column-family handling, slowdown behavior, priority, and memtable insert hints.

## Important APIs and Types
APIs include `setSync/sync`, `setDisableWAL/disableWAL`, `setIgnoreMissingColumnFamilies/ignoreMissingColumnFamilies`, `setNoSlowdown/noSlowdown`, `setLowPri/lowPri`, and `setMemtableInsertHintPerBatch/memtableInsertHintPerBatch`. There is a default constructor, a package-private non-owning native-handle constructor, and a shallow copy constructor.

## Control Flow, State, and Persistence
Options are stored in native memory. Setters mutate the native handle and return `this`; getters read native state. `sync` controls fsync-like durability, while `disableWAL` weakens crash recovery and backup assumptions. `noSlowdown` and `lowPri` affect behavior under write stalls/compaction lag.

## Dependencies and Integration Points
Depends on `RocksObject`, `Status.Code`, `RocksDB.write`, transactions, backup engine semantics, and JNI. Transactions can expose and update write options.

## Risks and Test Signals
The copy constructor is shallow for native pointer members. Disabling WAL can lose unflushed memtable data and requires flush-before-backup safety. `AbstractTransactionTest.writeOptions` verifies a transaction receives non-owning write options, preserves `disableWAL`, and reflects updated `sync` state.
