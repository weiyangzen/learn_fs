<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/Cargo.toml -->
# sources/storage-engines/tikv/components/file_system/Cargo.toml

Purpose: this manifest defines the `file_system` crate, a TiKV workspace component that wraps filesystem APIs with I/O typing, statistics, rate limiting, checksums, and recovery-space helpers.

Important build surface: features include `bcc-iosnoop` for optional BCC/eBPF disk tracing, `failpoints`, and `testexport`. Dependencies include `fs2` for file allocation/locking, `crc32fast`, `openssl`, `prometheus`, `prometheus-static-metric`, `online_config`, `parking_lot`, `crossbeam-utils`, `strum`, `tokio`, and Linux-only optional `bcc` plus `thread_local`.

Integration points: the crate exports replacements or wrappers for many `std::fs` functions, `File`, `OpenOptions`, `IoRateLimiter`, `IoBytesTracker`, I/O stats collectors, and `Sha256Reader`. It is used by external storage restore code and TiKV subsystems that need disk I/O accounting.

State and persistence behavior: the manifest itself has no state, but it enables code paths that reserve disk space, create/delete/sync files, and collect per-thread or eBPF I/O stats.

Risks: enabling `bcc-iosnoop` adds kernel/BCC dependencies and unsafe global state in the implementation. The crate uses `#![feature(test)]`, so test/bench builds require nightly features in TiKV's toolchain.

Test signals: dev dependency `tempfile` supports filesystem unit tests. Linux-only code is conditionally compiled based on target OS and features.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/Cargo.toml -->
