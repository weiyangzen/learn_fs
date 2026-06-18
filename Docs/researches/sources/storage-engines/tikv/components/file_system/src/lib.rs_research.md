<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/lib.rs -->
# sources/storage-engines/tikv/components/file_system/src/lib.rs

Purpose: this crate root re-exports instrumented filesystem APIs and implements common helpers for I/O typing, byte tracking, priorities, file operations, checksums, SHA-256 streaming, and disk-space reservation.

Important APIs and types: public exports include `File`, `OpenOptions`, `init_io_stats_collector`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, `MetricsManager`, `IoRateLimiter`, and rate-limit configuration types. `IoType` enumerates TiKV workload classes such as foreground reads/writes, flush, compaction, replication, import/export, and log rewrite. `WithIoType` temporarily sets the thread I/O type and restores it on drop. `IoBytesTracker` computes deltas from per-thread OS totals, tolerating initial fetch failures. `IoPriority` is serializable/deserializable and convertible to/from `online_config::ConfigValue`.

Control flow: utility functions wrap file operations through instrumented `File`: `write`, `read`, `read_to_string`, `copy`, `copy_and_sync`, deletion/creation helpers, `sync_dir`, CRC32 helpers, and `reserve_space_for_recover`. `Sha256Reader` wraps sync or async readers and updates a shared OpenSSL hasher as bytes are read. `reserve_space_for_recover` maintains a `space_placeholder_file`, reallocating it if size changes and deleting partial files on allocation failure.

State and persistence behavior: `WithIoType` manipulates thread-local state in the selected I/O stats implementation. File helpers persist data and can fsync destination files/directories in `copy_and_sync` and reservation paths. `IoBytesTracker` stores previous/current counters in memory only.

Dependencies and integration points: it integrates `crc32fast`, `openssl`, `online_config`, `serde`, `tokio::io::AsyncRead`, and internal modules. External storage uses `File` and `Sha256Reader` for restore output and checksum validation.

Risks: several helpers assume file sizes fit in `usize` for buffer preallocation. `sync_dir` opens paths through the instrumented `File`, so it captures current limiter state. `IoBytesTracker::update` subtracts current from previous without saturating, assuming proc counters are monotonic. `reserve_space_for_recover` relies on filesystem allocation support and deletes the placeholder on failure.

Test signals: tests cover file size/existence/deletion, directory creation/deletion, directory sync, CRC32 on small/large files, SHA-256 reader behavior, and reserve-space allocation failure through `file.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/lib.rs -->
