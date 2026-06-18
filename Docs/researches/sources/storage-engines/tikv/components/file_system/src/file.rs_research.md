<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/file.rs -->
# sources/storage-engines/tikv/components/file_system/src/file.rs

Purpose: this module wraps `std::fs::File` and `std::fs::OpenOptions` so file reads and writes can be throttled by the global `IoRateLimiter` using the current thread's `IoType`.

Important APIs and types: `File` stores an inner `fs::File` and an optional `Arc<IoRateLimiter>` captured at open/create time. Constructors include `open`, `create`, `from_raw_file`, `try_clone`, and test-only variants with explicit limiters. It forwards sync, metadata, permissions, length, allocation, duplication, and file-locking methods. `OpenOptions` mirrors standard open options and implements Unix `OpenOptionsExt` on Linux.

Control flow: `Read::read` and `Write::write` check whether a limiter was captured. If present, they loop until the requested buffer is consumed or EOF/zero write occurs, asking `limiter.request(get_io_type(), IoOp::Read/Write, remains)` for the next allowed chunk. Without a limiter, operations delegate directly to the inner file. `Seek` and `flush` are transparent delegates.

State and persistence behavior: the wrapper does not add persistence semantics beyond the inner file, except that write throughput may be sliced and delayed. It snapshots the global limiter when the file is created or opened; later calls to `set_io_rate_limiter` do not affect existing `File` instances.

Dependencies and integration points: it integrates `fs2::FileExt`, crate-level `IoOp`, `IoRateLimiter`, `get_io_rate_limiter`, and `get_io_type`. The crate root re-exports `File` and `OpenOptions`.

Risks: limiter requests are based on the full remaining buffer, but the underlying OS read/write may return less, so statistics can include EOF reads, as the tests document. Existing files may keep an old limiter after global replacement. Blocking rate limiting occurs in synchronous read/write calls.

Test signals: `test_instrumented_file` verifies throttled writes/reads and statistics by I/O type. `test_unix_file_allocate_failure` validates allocation error behavior for zero length on Unix.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/file.rs -->
