# sources/test-tools/fio/engines/rados.c

## Purpose
`rados.c` implements fio's `rados` ioengine for benchmarking Ceph object storage through the low-level librados API. It is diskless from fio's perspective: fio file names become RADOS object names, object sizes are synthesized from job size and file count, and open/invalidate hooks are no-ops because the engine owns all storage access through a Ceph pool.

## Important APIs, Types, And Functions
The engine state is `struct rados_data`, holding the `rados_t` cluster handle, `rados_ioctx_t`, completion event array, pthread condition/mutex pair, completion list, and scheduled/completed counters. Per-I/O state is `struct fio_rados_iou`, attached to `io_u->engine_data`, with a completion handle and optional write op for TRIM. `struct rados_options` exposes `clustername`, `pool`, `clientname`, `conf`, `busy_poll`, and `touch_objects`.

`_fio_setup_rados_data()` allocates shared state and completion storage. `_fio_rados_connect()` creates the Ceph client, reads config, connects, opens the pool IO context, sizes fio files, and optionally touches objects. `_fio_rados_disconnect()` tears handles down. `fio_rados_queue()` submits `rados_aio_write`, `rados_aio_read`, or zeroing write-op TRIM requests. `complete_callback()` records completions into a protected list. `fio_rados_getevents()` drains completed `fio_rados_iou` nodes into `aio_events`.

## Control Flow
Fio calls `.setup`, which allocates `rados_data`, forces thread mode, connects to Ceph, creates/touches objects, and records synthetic file sizes. Each `io_u` receives a `fio_rados_iou` in `.io_u_init`. On `.queue`, the engine creates a librados completion, submits async operation by object name and offset, increments `ops_scheduled`, and returns `FIO_Q_QUEUED`. Librados invokes `complete_callback`, which appends the per-I/O node and signals waiters. `.getevents` waits until `min` events exist, releases librados completion/write-op resources, and returns event count; `.event` maps event indexes back to fio `io_u`s.

## State And Persistence
State is process-local except for Ceph objects. The engine creates/touches objects on connect and unconditionally removes all job objects during cleanup via `_fio_rados_rm_objects()`, so benchmark data is transient. Completion state is protected by `completed_lock`; `ops_scheduled` and `ops_completed` gate cleanup so resources are not destroyed before callbacks finish.

## Dependencies And Integration Points
This file depends on `librados`, pthreads, fio ioengine hooks, `flist`, fio logging/error helpers, and option grouping from `optgroup.h`. It registers a `FIO_DISKLESSIO` engine named `rados` using `register_ioengine()`.

## Risks
`busy_poll` is accepted but not used by `getevents`, which always waits on the condition variable when completions are absent. Cleanup removes every object named in the fio job, so accidental use against existing objects is destructive. `fio_rados_io_u_init()` does not check `calloc` failure before dereferencing. Error cleanup in `_fio_rados_connect()` can leave a created cluster handle if failure happens before `rados_create` succeeds. Timeouts passed to `getevents` are ignored.

## Test Signals
Useful tests include a missing pool/name config failure, read/write/TRIM submission against a test Ceph pool, cleanup waiting with in-flight callbacks, and ensuring object removal behavior is explicit. Unit-style tests can exercise option parsing and allocation-failure paths, but full confidence needs an integration Ceph cluster.
