<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.c -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.c

Purpose: this BCC/eBPF C program tracks block I/O bytes and latency per TiKV `IoType`. It is compiled and loaded by `biosnoop.rs` when the `bcc-iosnoop` feature is enabled.

Important APIs and data structures: `stats_t` stores read/write bytes. `io_type` mirrors Rust `IoType` values. `info_t` stores I/O type and start timestamp per kernel `request`. BPF maps include `info_by_req`, `type_by_pid`, and `stats_by_type`, plus per-type read/write latency histograms.

Control flow: `trace_req_start` runs on `blk_account_io_start`, filters by the TiKV process TGID placeholder, reads the current thread's `io_type *` from `type_by_pid`, stores the type and timestamp in `info_by_req`, and defaults to `Other` if unavailable. `trace_req_completion` runs on `blk_account_io_completion`, looks up request info, detects read/write using kernel-version-compatible request flags, increments byte counters, buckets latency in microseconds using `bpf_log2l`, updates the matching histogram, deletes the request info, and exits.

State and persistence behavior: all state is in BPF maps in kernel memory and is consumed by the Rust wrapper. It is not persistent across process restarts or BPF detach.

Dependencies and integration points: it relies on Linux block-layer probe symbols, BCC macros, a Rust-substituted `##TGID##`, and the `type_by_pid` map being populated with user-space addresses of Rust `IoType` slots.

Risks: the C enum must stay exactly aligned with Rust `IoType`; the comment notes auto-generation is TODO. A concrete bug is visible in the `LevelZeroCompaction` write case: it calls `level_zero_replication_write_latency.increment(...)`, but the declared histogram is `level_zero_compaction_write_latency`; this looks like a compile/load failure or missing metric update depending on BCC handling. Kernel API compatibility is fragile around request flag fields and probe symbol names.

Test signals: no tests in the C file itself; Rust `biosnoop.rs` tests exercise compilation/loading and I/O accounting when BCC is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.c -->
