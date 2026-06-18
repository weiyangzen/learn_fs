<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/mod.rs -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/mod.rs

Purpose: this module selects the platform-specific I/O statistics implementation and provides a stub for unsupported targets.

Important APIs: it re-exports `init`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, and `get_thread_io_bytes_total` from one of three implementations: a stub, `biosnoop`, or `proc`. The stub maintains a thread-local `IoType`, returns zero bytes, and reports `init` failure with "No I/O tracing tool available".

Control flow: conditional compilation chooses the implementation. Non-Linux or feature combinations that are not `target_os = "linux"` with or without `bcc-iosnoop` get the stub. Linux with `bcc-iosnoop` uses eBPF/BCC; Linux without that feature uses `/proc` polling. Test-only aligned `A512` supports O_DIRECT tests.

State and persistence behavior: the module itself has no state beyond the selected implementation. The stub's only state is thread-local I/O type.

Dependencies and integration points: the crate root re-exports these APIs for `WithIoType`, `File`, metrics, and `IoBytesTracker`. The chosen implementation determines whether byte metrics come from OS accounting or zeros.

Risks: the `cfg(not(any(target_os = "linux", feature = "bcc-iosnoop")))` condition means enabling `bcc-iosnoop` on a non-Linux target suppresses the stub while the Linux+BCC module is not selected, which can create missing exports if such a build is attempted. Operational semantics differ significantly between stub, proc, and BCC collectors.

Test signals: benchmarks exercise `fetch_io_bytes` and `set_io_type` under spawned threads. Platform-specific deeper tests live in `proc.rs` and `biosnoop.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/mod.rs -->
