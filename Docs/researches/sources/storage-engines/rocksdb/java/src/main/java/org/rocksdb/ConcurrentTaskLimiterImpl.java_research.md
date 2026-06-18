# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiterImpl.java

Purpose: concrete JNI implementation of `ConcurrentTaskLimiter`. Constructor creates a named native limiter with a maximum outstanding task count.

Control flow asserts ownership before forwarding `name`, `setMaxOutstandingTask`, `resetMaxOutstandingTask`, and `outstandingTask` calls to native code. Setters return the base type for fluent use. State is fully native and can affect task admission in RocksDB subsystems that use the limiter. Dependencies include `ConcurrentTaskLimiter`, `RocksObject` disposal, and JNI symbols.

Risks: ownership assertions may be disabled, concurrent updates rely on native synchronization, and the typo in the abstract parameter name is harmless but can obscure API review. Tests should verify construction, name persistence, zero/negative/positive limit semantics, outstanding count observation during task execution, and native disposal.
