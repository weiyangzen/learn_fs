# sources/storage-engines/foundationdb/fdbrpc/AsyncFileEIO.h

Purpose: Unix libeio-backed implementation of `IAsyncFile`, selected as `Net2AsyncFile`. It provides asynchronous open/read/write/truncate/sync/size/delete/rename/stat operations and a generic dispatch path through the EIO thread pool.

Important APIs and type: `AsyncFileEIO` implements `IAsyncFile`. Static APIs include `init`, `stop`, `should_poll`, `open`, `deleteFile`, `renameFile`, `lastWriteTime`, `async_fsync_parent`, `async_fdatasync`, `async_fsync`, `waitAndAtomicRename`, and `dispatch`. Instance APIs wrap file operations and metrics. Private helpers include `openFlags`, `error`, `read_impl`, `write_impl`, `truncate_impl`, `sync_impl`, `size_impl`, `stat_impl`, `dispatch_impl`, `poll_eio`, and callbacks.

Control flow: file operations submit EIO requests with a `Promise<Void>`, await completion, cancel on actor cancellation, restore task priority through `delay(0, taskID)`, then translate EIO results to Flow errors. Atomic create writes to `<filename>.part` and renames after fsync plus parent directory fsync.

State and persistence behavior: each instance owns an fd, flags, filename, deferred `ErrorInfo`, and logical read/write metrics. Persistent effects are normal filesystem writes, truncates, renames, deletes, and fsyncs.

Dependencies and integration points: depends on libeio, Flow actors/futures, `IAsyncFile`, TD metrics, POSIX file APIs, and Apple `F_FULLFSYNC` custom handling. `eio_want_poll` schedules main-thread polling at `TaskPriority::PollEIO`.

Risks: write/truncate errors can be deferred through `ErrorInfo` and surface on sync, so callers must sync to observe durability failures. Correctness depends on polling callback scheduling. O_DIRECT is conditional on knobs and flags.

Test signals: no direct tests in this subset; file-system tests elsewhere usually validate `IAsyncFile` contracts and atomic write behavior.
