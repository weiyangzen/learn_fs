# sources/storage-engines/raft-engine/src/file_pipe_log/pipe.rs

## Purpose
This file implements the active filesystem log pipe. `SinglePipe` manages one monotonic queue of log files for either append or rewrite traffic; `DualPipes` combines append and rewrite pipes and implements the `PipeLog` trait consumed by the raft engine.

## Important APIs, Types, And Functions
`PathId`, `Paths`, `DEFAULT_PATH_ID`, and `DEFAULT_FIRST_FILE_SEQ` define how physical directories and file sequences are represented. `File<F>` records an opened file's sequence, shared handle, format, directory index, and whether it is a reserved recycled file. `WritableFile<F>` tracks the currently writable sequence, writer, and format.

`SinglePipe::open` creates or opens the last active file for writes, initializes metrics, installs active and recycled queues, and posts `EventListener::post_new_log_file` for existing active files. `append`, `read_bytes`, `sync`, `rotate`, `purge_to`, `file_span`, and `total_size` provide the queue operations behind `PipeLog`.

`rotate_imp` is the core rollover routine. It closes the current writer, reuses a recycled file or creates a new file, writes and syncs the new header, syncs the directory, swaps the writable file, appends the new active `File`, updates metrics, and notifies listeners.

`recycle_file` renames a reserved or purged file into the next queue filename and reopens it for read-write use. `new_file` selects a directory with enough free space and creates a fresh file. `find_available_dir` checks spill directories via `fs2::statvfs`, falling back to the main directory.

`DualPipes` stores exactly two `SinglePipe`s, with append at index `LogQueue::Append as usize` and rewrite at index `LogQueue::Rewrite as usize`, plus directory lock files that are unlocked on drop.

## Control Flow
Writes call `DualPipes::append`, dispatch by queue, and enter `SinglePipe::append`. The writable mutex is acquired first; if the current offset reached `target_file_size`, rotation happens before writing. The batch receives a `LogFileContext`, can emit alignment padding under V2 signing, and writes its bytes. On a no-space error, the writer truncates back, rotates to another file if possible, and returns `Error::TryAgain` so the caller can retry on the new file. Successful writes return a `FileBlockHandle` and trigger append listeners.

Reads call `get_fd` to validate the requested sequence lies in the active contiguous span, then build a `LogFileReader` over the shared handle and read the requested block. Purges split `active_files` at the requested sequence, retain the tail, and either move eligible V2 signed files into the recycled queue or delete them. Append queue recycling is capacity-limited; rewrite queue capacity is always zero.

Shutdown closes the active writer and best-effort renames non-reserved recycled append files into reserved filenames to reduce future recovery cost. Directory locks are released by `DualPipes::drop`.

## State And Persistence Behavior
The persistent state is the set of queue files on disk, their headers, and possible reserved files. `active_files` and `recycled_files` are concurrent `RwLock<VecDeque<_>>` structures; `writable_file` is a mutex and must be acquired first when both active file state and writer state are needed. New log headers are synced before the new file becomes active, and the containing directory is synced on Unix-like systems.

Recycling is conservative: only files with log signing are reused, and recycle capacity is derived from append queue configuration. Purged files outside capacity or with incompatible formats are deleted. Active file sequences are expected to be contiguous; range checks and scan-time cleanup in the builder enforce this invariant.

## Dependencies And Integration Points
The pipe relies on `Config` for target file size and recycle settings, `FileSystem` for file operations, `EventListener` for lifecycle callbacks, `metrics` and `perf_context` for observability, `LogFileWriter`/`LogFileReader` for format-aware I/O, and `ReactiveBytes` for delayed signing of write buffers. It is built by `DualPipesBuilder::finish` and used by `Engine` through the `PipeLog` trait.

## Risks And Edge Cases
No-space handling has documented corner cases when a single write is larger than the target file size and multiple directories or recycled logs are involved. Directory sync uses `unwrap`, so a directory fsync failure panics rather than returning an error. `get_fd`, `purge_to`, and `file_span` assume at least one active file. Recycled file rename failures are handled by deleting the source and falling back, which may reduce recycle capacity. The index-based `DualPipes` dispatch depends on enum discriminants and is guarded by debug assertions only.

## Test Signals
`test_dir_lock` verifies exclusive directory locking. `test_pipe_log` covers initial file creation, rollover, purge range validation, append offsets, reads, and invalid read handles. `test_pipe_log_with_recycle` exercises purge-to-recycle, unreadability of old handles, reuse, and data integrity under an obfuscated filesystem. `test_release_on_drop` verifies lock release.
