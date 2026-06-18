# sources/storage-engines/raft-engine/src/file_pipe_log/pipe_builder.rs

## Purpose
`pipe_builder.rs` discovers existing log files, locks directories, recovers logical state by replaying log batches, prepares recycled files, and finally constructs `DualPipes`. It is the startup and recovery coordinator for the filesystem-backed pipe log.

## Important APIs, Types, And Functions
`ReplayMachine` is the recovery extension trait. `replay` consumes each decoded `LogItemBatch` with its `FileId`; `merge` combines a machine that consumed newer items from the same queue. The associativity requirement allows parallel recovery over chunks.

`DefaultMachineFactory<M>` adapts any default `ReplayMachine` to the crate's `Factory` trait. `RecoveryConfig` bundles queue, recovery mode, concurrency, and read block size. `DualPipesBuilder<F>` owns `Config`, `FileSystem`, listeners, scanned directories and locks, parsed file names, and opened file handles.

`scan` calls `scan_and_sort`, opens append and rewrite files read-only except for last files or `TolerateAnyCorruption`, opens reserved files read-only, removes non-contiguous leading spans, and clears obsolete metadata before the first retained sequence. `scan_dir` creates or validates directories, optionally locks them, and classifies filenames as append, rewrite, or reserved.

`recover` allocates a bounded rayon thread pool, splits threads between append and rewrite queues, and invokes `recover_queue_imp` for both queues in parallel. `recover_queue_imp` chunks files, opens each file with `LogItemBatchFileReader`, replays decoded batches, tolerates and truncates corruption according to `RecoveryMode`, and reduces chunk machines with `ReplayMachine::merge`.

`initialize_files` pre-fills reserved recycle files up to configured capacity and removes excess reserved files. `finish` creates append and rewrite `SinglePipe`s and wraps them in `DualPipes`. `lock_dir` creates and exclusively locks the lock file under a directory.

## Control Flow
Startup normally calls `new`, `scan`, `recover`, and `finish`. Scanning fills file-name vectors, sorts by sequence, opens handles, and prunes invalid prefix ranges caused by holes or duplicates. Recovery then reads append and rewrite queues in parallel. Within each file, `LogItemBatchFileReader::open` parses the file header and records the format back into `File<F>`. Each item batch is replayed, with a lookahead read used to identify the last batch and verify its entry block before committing it to the replay machine.

If a file header or batch is corrupted, behavior depends on `RecoveryMode`: absolute consistency fails immediately; tail corruption mode truncates only the final file; tolerate-any mode may truncate any corrupted file. Entry-block checksum or decompression failures on the last item are handled similarly, truncating to the batch header offset in non-absolute modes.

After recovery, `finish` initializes reserved files and opens `SinglePipe`s. Append receives the reserved files for later recycling; rewrite receives no recycled files.

## State And Persistence Behavior
The builder mutates on-disk state during recovery when configured to tolerate corruption, using `truncate` and `sync` on broken files. It may create missing directories, create lock files, prefill reserved files with zeros up to `target_file_size`, and delete excess reserved files. It also deletes stale metadata from old file-system implementations once it identifies a retained active range.

Opened `File<F>` entries initially carry `LogFileFormat::default`; recovery updates each format after parsing the header. This matters because later purge/recycle logic only recycles files whose parsed version supports log signing.

## Dependencies And Integration Points
The builder connects `Config`, `RecoveryMode`, `FileSystem`, `Handle`, `EventListener`, `LogItemBatch`, `FileId`, `LogQueue`, `LogFileReader`, `LogItemBatchFileReader`, and `SinglePipe`. It uses `rayon` for parallel replay, `fs2` for locking, and the filename helpers from `format`. `Engine::open` and tooling such as `fork` depend on its scan and finish behavior.

## Risks And Edge Cases
The file-hole cleanup drains everything before the last detected gap, so duplicated or missing sequences can discard older files from consideration. The stale metadata deletion uses sampling to find a start point and may leave metadata if the sample misses it. Prefill writes fixed-size zero buffers and can stop early on no-space, then reset target recycle capacity to zero for that run. `from_script`-style replay machines can make merge errors visible only during parallel reduction. Recovery read concurrency of zero returns an empty machine without validating files.

## Test Signals
Direct tests for `pipe_builder.rs` are mostly reached through pipe, engine, recovery, and fork tests. Relevant covered behavior includes directory locking, open/recover/finish through `new_test_pipes`, recycle prefill/reuse behavior, and corruption-handling tests elsewhere that rely on `recover_queue_imp` truncation semantics.
