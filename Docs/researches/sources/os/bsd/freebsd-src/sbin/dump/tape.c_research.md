# File Research: sources/os/bsd/freebsd-src/sbin/dump/tape.c

Implements dump output buffering, tape/media volume handling, worker process I/O, write recovery, and tape-level checkpoints.

Key responsibilities:
- Allocates tape buffers and request arrays with `alloctape()`.
- Accepts logical tape records from traversal via `writerec()` and disk block references via `dumpblock()`.
- Flushes full tape records to worker processes with `flushtape()`.
- Handles end-of-tape, volume changes, rewinds, and roll-forward replay.
- Creates a checkpointing child per tape volume in `startnewtape()` so a failed volume can be rewritten from saved process state.
- Creates three worker processes with `create_workers()` to overlap disk reads and tape writes.
- Implements worker-side disk read and tape write loop in `worker()`.

Important data:
- `u_spcl`: dump protocol header union shared with `traverse.c`.
- `curino`, `newtape`: current inode and volume state used globally.
- `workers[WORKERS+1]`: per-worker request and data buffers, with one extra buffer for roll-forward reconstruction.
- `wp`, `nextblock`, `trecno`: current master-side buffer position.
- `lastspclrec`, `blocksthisvol`, `asize`: media accounting.

Concurrency model:
- Parent/master sends `struct req` arrays through socketpairs.
- Workers reopen the disk for independent seek pointers.
- Workers synchronize write order with a `SIGUSR2` ring and `setjmp`/`longjmp`.
- Tape errors signal the master with `SIGUSR1`; aborts signal `SIGTERM`.

Output modes:
- stdout pipe.
- `popen()` pipeline, with `DUMP_VOLUME` environment variable set per volume.
- local file/device.
- remote tape through `rmtopen()`/`rmtwrite()` when RDUMP is enabled.

Recovery behavior:
- Short writes are treated as EOT.
- `rollforward()` reconstructs pending requests after EOT and starts the next volume.
- `tperror()` asks the operator whether to restart; successful restart exits with `X_REWRITE` to parent checkpoint logic.

Risks and constraints:
- Heavy reliance on global state and fork-time process snapshots.
- Worker synchronization depends on signals and process ordering.
- EOT in final tape records is largely punted with an error asking for larger media or no size estimate.
- Pointer arithmetic on `void *`-like buffers is C-extension-friendly but not purely ISO C.
