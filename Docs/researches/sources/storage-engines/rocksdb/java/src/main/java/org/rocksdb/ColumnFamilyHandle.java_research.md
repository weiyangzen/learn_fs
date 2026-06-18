# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyHandle.java

- **Purpose:** Java wrapper for native RocksDB `ColumnFamilyHandle` pointers.
- **Important APIs/types/functions:** Constructors create owned handles tied to a `RocksDB` parent or non-owning handles from JNI. Public APIs include `getName()`, `getID()`, and `getDescriptor()`. Equality/hash use DB native handle, column-family ID, and name. `disposeInternal()` frees the handle only if the parent DB still owns its handle.
- **Control flow:** Owned constructor retains the parent DB to bias lifecycle ordering. JNI constructor disowns the native handle because Java likely already has an owner. Accessors assert owned/default handle and delegate to JNI. `isDefaultColumnFamily()` compares against `rocksDB_.getDefaultColumnFamily()`.
- **State and persistence behavior:** Native handle identifies a column family inside a live DB. Java retains parent DB reference; no durable state is stored here.
- **Dependencies:** Depends on `RocksDB`, `ColumnFamilyDescriptor`, `RocksObject`, `RocksDBException`, `Arrays`, and `Objects`.
- **Integration points:** Used across reads/writes/options/metadata APIs to select a column family. JNI-created non-owning handles appear in callbacks/descriptors.
- **Risks:** `equals`, `hashCode`, and `isDefaultColumnFamily()` assume `rocksDB_` is non-null, so non-owning JNI-created handles are risky in those paths. Closing the DB before handles skips native handle deletion to avoid double-free. Exceptions in equality/hash are wrapped as runtime exceptions.
- **Test signals:** Name/ID/descriptor retrieval, equality/hash for handles from the same and different DBs, default column-family behavior, non-owning handle safety, and close ordering with DB close.
