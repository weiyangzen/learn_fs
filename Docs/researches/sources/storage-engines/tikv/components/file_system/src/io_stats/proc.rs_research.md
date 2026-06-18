<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/proc.rs -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/proc.rs

Purpose: this module implements the default Linux I/O stats collector by reading `/proc/<pid>/task/<tid>/io` and attributing per-thread byte deltas to the current `IoType`.

Important APIs and types: `ThreadId` stores process id, thread id, and an optional cached `BufReader<File>` over the proc file. `LocalIoStats` stores a `ThreadId`, current I/O type, and last flushed bytes. `AtomicIoBytes` stores global per-type counters. Public APIs are `init`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, and `get_thread_io_bytes_total`.

Control flow: `ThreadId::fetch_io_bytes` lazily opens the proc file, seeks back to the start, parses `read_bytes` and `write_bytes`, and returns totals. `init` verifies proc access, initializes the current thread's sentinel, and hooks TiKV thread startup to create sentinels for new threads. `set_io_type` flushes the current thread's delta into the old type before changing the thread-local and sentinel type. `fetch_io_bytes` flushes every thread-local sentinel and returns global totals.

State and persistence behavior: byte counters are process-local atomics. Per-thread sentinels are held in `ThreadLocal<CachePadded<Mutex<LocalIoStats>>>`. The proc reader is cached per thread. No state is persisted beyond process memory.

Dependencies and integration points: it uses TiKV thread IDs/hooks, `thread_local`, `parking_lot`, and crate-level `IoBytes`/`IoType`. It is selected on Linux when `bcc-iosnoop` is not enabled.

Risks: attribution depends on callers setting `IoType` before disk work; untagged threads accumulate under `Other`. Reading `/proc` can fail due to permissions, process/thread races, or nonstandard environments. Global counters only increase when flushed, so stale threads that never change type are flushed by `fetch_io_bytes`, but dead-thread edge cases depend on `ThreadLocal` iteration behavior.

Test signals: tests use O_DIRECT reads/writes against temp files to verify proc byte deltas, thread I/O type attribution, and current-thread total fetching. These tests are Linux and filesystem dependent.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/proc.rs -->
