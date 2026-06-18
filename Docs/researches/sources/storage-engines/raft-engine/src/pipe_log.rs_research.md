# sources/storage-engines/raft-engine/src/pipe_log.rs

Purpose: this file defines the generic log storage abstraction used by raft-engine. It provides the queue/file identifiers, block handles, format version behavior, context-sensitive bytes, and the `PipeLog` trait consumed by engine, purge, recovery, and tests.

Important APIs and types: `LogQueue` distinguishes `Append` and `Rewrite`. `FileSeq` is the per-queue sequence type. `FileId` identifies a queue/sequence pair and orders by freshness, treating append files as newer than rewrite files when queues differ. `FileBlockHandle` points to a byte range in a log file. `Version` is a serde-repr enum with `V1` and `V2`; `has_log_signing` enables signing for V2 and can be forced by failpoint. `LogFileContext` carries `FileId` plus version and derives an optional signature. `ReactiveBytes` lets append payloads depend on the target file context. `PipeLog` defines `read_bytes`, `append`, `sync`, `file_span`, `file_at`, `total_size`, `rotate`, and `purge_to`.

Control flow: a log implementation appends `ReactiveBytes` to a queue and returns a `FileBlockHandle`. For reactive payloads, the implementation supplies `LogFileContext` before serializing bytes. `file_at` clamps a ratio to `[0, 1]`, calculates the current file count from `file_span`, and returns the sequence at that percentile. Purge callers use `purge_to` to remove all files older than a given `FileId` within that queue.

State and persistence behavior: this file stores no log data itself, but its contracts describe persistence boundaries. Append and rewrite queues are independent sequence spaces; `FileBlockHandle` is the durable locator stored in memtables. `Version::V2` adds per-file signing through `LogFileContext::get_signature`, currently the low 32 bits of the file sequence.

Dependencies and integration points: depends on `fail`, `num_traits`, `num_derive`, `serde_repr`, `strum`, and the crate `Result`. It is used by memtable entry locations, purge watermarks, engine log reads/writes, event listeners, stress hooks, and test utilities.

Risks and invariants: the `Ord` implementation intentionally imposes cross-queue freshness semantics; code that wants pure sequence ordering must compare only within a queue. `get_signature` assumes file counts stay below `u32::MAX` for practical signing uniqueness. `file_at` uses floating-point truncation and includes the active file in the count, so purge callers must clamp to `active_file - 1` when the active file is not purgeable.

Test signals: no direct tests in this file. Dummy constructors for `FileId` and `FileBlockHandle` are test-only and are used heavily by memtable and write-path tests. Failpoints can force V2 signing behavior.
