# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Env.java

Purpose: abstract base for RocksDB environment implementations. It exposes the default environment and background thread-pool controls, queue length, IO/CPU priority lowering, and thread-list inspection.

Control flow for `getDefault()` uses an `AtomicReference<RocksEnv>` and CAS loop. It loads the library, creates a `RocksEnv` around the native default env, then calls `disOwnNativeHandle()` because C++ owns the singleton. Other methods forward native calls with `Priority` byte values. State includes only the Java singleton reference; thread pools and env resources are native. Integration points include `DBOptions.setEnv`, `EnvOptions`, `RocksEnv`, `ThreadStatus`, and background flush/compaction execution.

Risks: default env must never be freed by Java, CAS loop must avoid leaking multiple temporary wrappers, priority byte mapping must match native, and thread-list retrieval can throw `RocksDBException`. Tests should cover singleton identity, no-op disposal of default env, thread-pool setters/getters, priority lowering calls, and concurrent `getDefault()` access.
