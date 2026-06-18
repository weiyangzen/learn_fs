# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTableFilter.java

- **Purpose:** Base Java callback wrapper for RocksDB table filters.
- **Important APIs/types/functions:** Extends `RocksCallbackObject` and implements `TableFilter`. Constructor delegates to the callback base. `initializeNative(...)` creates the native table-filter callback object via `createNewTableFilter()`.
- **Control flow:** Instantiation calls into `RocksCallbackObject`, which invokes `initializeNative`; the native side later calls the `TableFilter` methods implemented by subclasses.
- **State and persistence behavior:** The Java object owns a native callback handle managed by `RocksCallbackObject`. It keeps no Java-side table state.
- **Dependencies:** Depends on `RocksCallbackObject`, `TableFilter`, and JNI implementation of `createNewTableFilter`.
- **Integration points:** Plugs Java filtering logic into native RocksDB table-processing paths.
- **Risks:** Subclasses must remain alive as long as native RocksDB may callback. Disposal order is important; premature close can leave native code with an invalid callback target.
- **Test signals:** Creating a concrete filter, verifying native handle allocation, exercising callback invocation from table-reader code, and closing while no database references remain.
