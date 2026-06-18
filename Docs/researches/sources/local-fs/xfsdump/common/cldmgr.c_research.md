# File Research: sources/local-fs/xfsdump/common/cldmgr.c

Purpose: manages child pthreads used by xfsdump/xfsrestore stream work.

Key behavior:
- Maintains a fixed `cld[CLD_MAX]` table, where `CLD_MAX = STREAM_SIMMAX * 2`.
- `cldmgr_init` clears the table, resets the stop flag, and records the parent thread id.
- `cldmgr_create` must be called by the parent thread. It finds an available slot, initializes child metadata, and creates a pthread running `cldmgr_entry`.
- `cldmgr_entry` registers the thread with the stream layer when `streamix >= 0`, calls the user entry function, and uses pthread cleanup to record exit state.
- `cldmgr_cleanup` marks a child as exited and signals the main process with `SIGUSR1`.
- `cldmgr_join` joins exited children, reports non-normal exit codes, unregisters stream threads with `stream_dead`, and resets slots for reuse.
- Provides stop and introspection helpers: `cldmgr_stop`, `cldmgr_stop_requested`, `cldmgr_remainingcnt`, and `cldmgr_otherstreamsremain`.

Interactions:
- Uses global `lock()`/`unlock()` around child table state.
- Integrates with `stream_register`/`stream_dead`.
- Uses `mlog` for process/thread diagnostics and `exit_codestring` for abnormal child exits.

Risks/notes:
- `cldmgr_stopflag` is a plain global boolean read by workers and written by the main thread; it relies on the program’s coarse synchronization and polling rather than atomics.
- `cldmgr_stop` intentionally avoids logging because it may be called while the main loop dialog owns logging locks.
- Child slot count is fixed; too many concurrent worker requests fail.
