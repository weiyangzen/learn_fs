# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractImmutableNativeReference.java

- **Purpose:** Thread-safe ownership base for immutable native references. It extends `AbstractNativeReference` and centralizes close-time release for Java objects that may or may not own a native C++ RocksDB pointer.
- **Important APIs/types/functions:** `owningHandle_` is an `AtomicBoolean`; constructor records ownership; `isOwningHandle()` exposes current ownership; `disOwnNativeHandle()` transfers/revokes deletion responsibility; `close()` atomically transitions owner to non-owner and calls subclass `disposeInternal()`.
- **Control flow:** Subclasses construct with an initial owner flag. Close is idempotent because only the successful `compareAndSet(true, false)` path releases native resources. Ownership transfer uses `disOwnNativeHandle()` before another wrapper or C++ owner is expected to delete the object.
- **State and persistence behavior:** State is in-memory Java ownership state plus the native object lifetime behind subclasses. There is no durable persistence, but incorrect ownership affects native memory persistence/leakage across JVM execution.
- **Dependencies:** Depends on `AbstractNativeReference` and `java.util.concurrent.atomic.AtomicBoolean`; release work is delegated to subclass JNI disposal.
- **Integration points:** Used by RocksDB Java wrappers needing immutable native handle ownership semantics, especially callback/native resource objects where double-free must be avoided.
- **Risks:** Misusing `disOwnNativeHandle()` leaks native memory; failing to call `close()` keeps native C++ memory live. Post-close method calls on subclasses are undefined by the base contract. Thread safety only protects the ownership flag, not subclass state.
- **Test signals:** Unit tests should exercise double close, ownership transfer before close, subclass `disposeInternal()` invocation exactly once, and try-with-resources behavior.
