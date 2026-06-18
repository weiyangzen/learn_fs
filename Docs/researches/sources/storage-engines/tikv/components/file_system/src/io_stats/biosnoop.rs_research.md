<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.rs -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.rs

Purpose: this module implements the optional Linux/BCC I/O stats collector. It loads `biosnoop.c`, attaches block I/O kprobes, maps TiKV threads to `IoType` slots, fetches per-type byte counters, and flushes latency histograms.

Important APIs and types: `BpfContext` owns the `BPF`, stats table, and type table. `IO_TYPE_ARRAY` is a global padded array of per-thread types with `MAX_THREAD_IDX + 1` slots. `IdxAllocator` assigns slots, and `IdxWrapper` frees them on thread-local drop. Public APIs are `init`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, `flush_io_latency_metrics`, and `get_thread_io_bytes_total` (currently unimplemented).

Control flow: `IDX` thread-local allocation registers the current thread id in the BPF `type_by_pid` table with a pointer to its slot. `set_io_type` writes the slot unless the overflow slot is used. `init` substitutes the process id into included C code, compiles it with BCC, attaches kprobes to `blk_account_io_start` and `blk_account_io_completion`, and stores tables in global `BPF_CONTEXT`. `fetch_io_bytes` iterates all Rust `IoType` values and reads `IoBytes` from the BPF table. `flush_io_latency_metrics` drains BPF histogram buckets into Prometheus histograms and zeros them.

State and persistence behavior: it uses unsafe mutable global BPF context and global thread-type slots. When all thread-local indices are freed, `IdxWrapper::drop` takes the BPF context to detach probes. Metrics are in-memory only.

Dependencies and integration points: it depends on `bcc`, `strum`, `crossbeam_utils`, TiKV thread helpers, and file-system metrics. `io_stats/mod.rs` selects this implementation for Linux with `bcc-iosnoop`.

Risks: unsafe global state and pointer sharing with eBPF require tight lifetime assumptions. More than 192 threads fall back to the reserved slot, always `Other`, losing attribution. `get_thread_io_bytes_total` returns unimplemented, so `IoBytesTracker` cannot use this collector for per-thread totals. The included C probe contains the `level_zero_replication_write_latency` typo, making the optional path risky until fixed.

Test signals: tests initialize BPF, run direct I/O reads/writes, validate per-type byte deltas, test thread-index allocation, flush latency metrics, and include a benchmark. They require kernel/BCC capabilities and can be environment-sensitive.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.rs -->
