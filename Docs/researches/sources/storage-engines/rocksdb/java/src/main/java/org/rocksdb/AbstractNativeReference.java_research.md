# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractNativeReference.java

- **Purpose:** Root contract for Java RocksDB objects that hold native C++ pointers. It documents explicit resource release and replaces any expectation of finalizer-based cleanup.
- **Important APIs/types/functions:** Implements `AutoCloseable`; declares protected `isOwningHandle()` and abstract `close()`.
- **Control flow:** There is no executable release implementation here. Subclasses define ownership checks and close behavior, usually by invoking JNI disposal when they own the native handle.
- **State and persistence behavior:** The class itself stores no state. Its contract governs native pointer lifetime, which is outside Java GC visibility and can persist until explicit close.
- **Dependencies:** Only Java `AutoCloseable`; subclasses such as `RocksObject`, `RocksMutableObject`, and callback objects implement the actual handle storage/disposal.
- **Integration points:** Base type for most RocksDB Java wrappers and try-with-resources use throughout the Java API.
- **Risks:** Forgetting to close resources leaks native memory/file handles. Calling methods after close has undefined behavior. The javadoc references finalization context but intentionally does not provide finalizer cleanup.
- **Test signals:** Static/API tests should verify wrappers implement `AutoCloseable`, document explicit close requirements, and throw or assert appropriately when methods are used after disposal in concrete subclasses.
