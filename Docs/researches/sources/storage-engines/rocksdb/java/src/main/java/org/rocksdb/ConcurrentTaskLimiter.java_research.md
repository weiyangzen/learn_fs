# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiter.java

Purpose: abstract native-backed base class for limiting concurrent background tasks. APIs define `name()`, `setMaxOutstandingTask(int)`, `resetMaxOutstandingTask()`, and `outstandingTask()`.

Control flow is polymorphic: the base class only stores the native handle via `RocksObject`; concrete classes implement JNI behavior. State is native limiter state, shared with RocksDB components that consult outstanding task counts. It is not Java-persisted. Dependencies include `RocksObject` and concrete `ConcurrentTaskLimiterImpl`.

Risks: API documentation says `0` blocks new tasks and negative means unlimited, but enforcement is native. Tests should cover concrete implementation behavior, limit changes under concurrent tasks, disposal, and any DB options that accept a limiter.
