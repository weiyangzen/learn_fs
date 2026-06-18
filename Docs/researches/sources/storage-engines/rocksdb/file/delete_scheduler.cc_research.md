# sources/storage-engines/rocksdb/file/delete_scheduler.cc

## Purpose
`delete_scheduler.cc` implements rate-limited file deletion for RocksDB. Instead of immediately removing every file, it can rename files to a `.trash` path, account for trash size, and delete them on a background thread with pacing, chunked truncation, directory fsync, and bucket-level wait support.

## Important APIs and control flow
`DeleteFile()` handles accounted files tracked by `SstFileManagerImpl`. It deletes immediately when rate limiting is disabled or trash size exceeds `max_trash_db_ratio`; otherwise it queues the file. `DeleteUnaccountedFile()` handles untracked files and deletes immediately when slow deletion is disabled or hard-link count is greater than one unless forced to background.

`AddFileToDeletionQueue()` calls `MarkAsTrash()`, updates `total_trash_size_` for accounted files, records stats, pushes a `FileAndDir` into `queue_`, updates pending counts and bucket counts, and signals the background thread. `MarkAsTrash()` appends `.trash`, resolves name conflicts under `file_move_mu_`, renames the file, and informs `SstFileManagerImpl` for accounted moves.

`BackgroundEmptyTrash()` waits on `cv_`, pops queued files, calls `DeleteTrashFile()` without holding `mu_`, records errors, applies a time penalty proportional to deleted bytes/rate, decrements pending and bucket counts, and signals waiters. `DeleteTrashFile()` can partially delete large single-link files with `Truncate()`/`Fsync()` chunks before full delete. `CleanupDirectory()` discovers existing trash files and either schedules them through an SFM or deletes immediately.

## State, persistence, and integration
State includes atomic rate/trash size/ratio, pending queues and buckets under `InstrumentedMutex`, background errors, stats pointer, and a lazily created `port::Thread`. Filesystem persistence changes are real renames/deletes/truncates through `FileSystem`, with optional directory fsync after final delete. Accounted file lifecycle is integrated with `SstFileManagerImpl::OnMoveFile`, `OnDeleteFile`, and `ScheduleFileDeletion`.

## Risks and test signals
Correctness depends on lock ordering across `mu_`, `file_move_mu_`, filesystem calls, and SFM callbacks. Destructor stops the background thread without guaranteeing all trash is emptied, leaving `.trash` files by design. Partial deletion is disabled for hard-linked files and depends on `NumFileLinks`, `ReopenWritableFile`, `Truncate`, and `Fsync` support. `CleanupDirectory()` must not double-account files if `OnAddFile()` succeeds but scheduling fails. Test signals include rate penalty timing, stats tick counts, conflict-name trash creation, background error collection, hard-link behavior, immediate deletion threshold, bucket wait signaling, and cleanup of existing trash files.
