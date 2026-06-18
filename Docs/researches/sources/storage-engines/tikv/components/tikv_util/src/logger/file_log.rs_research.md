# sources/storage-engines/tikv/components/tikv_util/src/logger/file_log.rs

## Purpose
Implements rotating file logging and archived-log cleanup for TiKV's logger backend.

## Important APIs, Types, And Functions
`open_log_file` creates parent directories and opens the active log file in append/create mode. `Rotator` defines the rotation lifecycle: `is_enabled`, `prepare`, `should_rotate`, `on_write`, and `on_rotate`. `RotatingFileLoggerBuilder` assembles a path, rename callback, cleanup limits, and rotators, then builds a `RotatingFileLogger`. `RotatingFileLogger` implements `Write`. `RotateBySize` is the built-in size-based rotator. `Runner` implements `worker::Runnable` for archive cleanup tasks.

## Control Flow
Building opens the active file, starts a lazy archive worker, schedules an initial archive pass, and prepares each enabled rotator from current file metadata. `write` updates all rotator state before writing bytes to the active file. `flush` checks rotators; on the first rotator requesting rotation, it flushes the file, asks the rename callback for an archive path, renames the active log, opens a fresh active file, resets all rotators, schedules archive cleanup, and returns. If no rotation is needed, it just flushes.

`Runner::list_old_logs` scans the log directory for files whose stems contain the active log prefix plus a parseable timestamp, sorts newest first, and returns metadata. `Runner::run` removes files exceeding `max_backups` and/or older than `max_days`.

## State And Persistence
Persistent state is the active log file, renamed archived log files, and deletion of old archives. In-memory state includes rotator counters, builder options, a lazy worker, and archive selection data.

## Dependencies And Integration
Depends on `chrono`, `ReadableSize`, `ReadableDuration`, TiKV `LazyWorker`, `Runnable`, and logger thread-name constants. It is used by `logger::file_writer`, which wraps the rotating logger in a `BufWriter`.

## Risks
Rotation happens during `flush`, not immediately during `write`; callers that do not flush may exceed configured rotation size. `RotateBySize` rotates only when `file_size > rotation_size`, so exactly equal size does not rotate. Rename or open failures propagate from `flush`; tests ensure they do not panic on drop. Archive timestamp parsing is filename-convention dependent and intentionally ignores malformed names. Cleanup uses `unwrap` around directory listing in the worker and logs remove failures.

## Test Signals
Tests cover size rotation threshold, rename failure behavior, max-backup cleanup at startup and after rotation, max-days cleanup at startup and after rotation, tolerance of illegal archive names, and timestamp extraction from valid and invalid filenames.
