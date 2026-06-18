# sources/test-tools/fio/engines/windowsaio.c

## Purpose
`windowsaio.c` implements fio's Windows asynchronous I/O engine using overlapped I/O and I/O Completion Ports. It supports either a background completion thread or direct dequeueing in `getevents`.

## Important APIs, Types, And Functions
`struct fio_overlapped` wraps `OVERLAPPED`, the owning `io_u`, and a completion flag. `struct windowsaio_data` stores the completion event array, IOCP handle, optional completion thread handle, event handle, and thread-running flag. `struct windowsaio_options` exposes `no_completion_thread`.

Important functions include `fio_windowsaio_init()` for IOCP/event/thread creation, `fio_windowsaio_open_file()` for Windows handle creation and IOCP association, `fio_windowsaio_queue()` for `ReadFile`/`WriteFile`/`FlushFileBuffers`, `fio_windowsaio_getevents_nothread()` for `GetQueuedCompletionStatusEx`, `fio_windowaio_getevents_thread()` for scanning completion flags signaled by `IoCompletionRoutine()`, and per-`io_u` init/free wrappers.

## Control Flow
`.init` allocates engine data and creates an IOCP. Unless `no_completion_thread` is set, it launches `IoCompletionRoutine`, optionally applying fio CPU affinity. `.open_file` chooses flags from direct/sync/fadvise/create options, opens the file with `FILE_FLAG_OVERLAPPED`, optionally invalidates cache by opening non-buffered, and associates the handle with the IOCP. `.queue` fills the overlapped offset, submits read or write, treats `ERROR_IO_PENDING` as queued, and handles sync directions by flushing immediately. Completion is either consumed directly from the IOCP in `.getevents` or marked by the helper thread and later harvested by scanning in-flight `io_u`s.

## State And Persistence
State is per fio thread and uses Windows kernel handles. File data persists normally. Each `io_u` owns a persistent `fio_overlapped` object for reuse across submissions.

## Dependencies And Integration Points
The engine depends on Win32 APIs, fio's Windows file fields (`fio_file->hFile`), generic size lookup, `win_to_posix_error`, option parsing, and fio's async event hooks.

## Risks
`fio_windowsaio_cleanup()` always waits on and closes `wd->iothread`; in no-completion-thread mode that handle may be unset. The background thread and cleanup coordinate through a plain Boolean and 250 ms polling. Direct-dequeue mode uses `GetLastError()` after `GetQueuedCompletionStatusEx`, but per-entry errors are usually in the overlapped status. Manual TRIM is unsupported. Cache invalidation is best effort and depends on no other open handles.

## Test Signals
Windows integration tests should exercise threaded and no-thread modes, direct/sync/fadvise open flags, read/write completion residuals, flush directions, invalid path/open failures, cleanup in both modes, and async error conversion. Unit-level tests can validate timeout wrap logic in `timeout_expired()`.
