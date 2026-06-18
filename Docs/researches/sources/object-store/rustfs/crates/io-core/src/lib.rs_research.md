# sources/object-store/rustfs/crates/io-core/src/lib.rs

Purpose: crate root and public facade for RustFS I/O core modules.

Important APIs: declares modules for backpressure, buffering, config, deadlock detection, direct I/O, priority queue, profiling, lock optimization, pool, reader, scheduler, shared memory, timeout wrapper, and writer. Re-exports the main public types such as `BytesPool`, `PooledBuffer`, `ZeroCopyObjectReader`, `ZeroCopyObjectWriter`, scheduler types/functions, `BackpressureMonitor`, `DeadlockDetector`, `LockOptimizer`, and timeout helpers. `DirectIoReader` is re-exported only on Linux.

Control flow and state: no runtime logic; this file controls public API shape and documentation.

Dependencies and integration: the module tree shows `io-core` as the shared lower-level I/O support crate. The example imports many items through these re-exports.

Risks: broad re-exports make API compatibility sensitive to internal module changes. Documentation says mmap zero-copy is a feature, but some reader paths copy into `Bytes`; public docs should stay aligned with implementation details.

Test signals: no direct tests. Compile coverage comes from module tests and external example usage.
