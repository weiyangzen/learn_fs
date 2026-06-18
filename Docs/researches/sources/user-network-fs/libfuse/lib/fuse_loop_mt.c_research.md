# sources/user-network-fs/libfuse/lib/fuse_loop_mt.c

## Purpose

`fuse_loop_mt.c` implements libfuse's multithreaded low-level session loop and the private loop-configuration API introduced for FUSE 3.12. It dynamically creates worker threads to receive and process kernel requests, optionally clones `/dev/fuse` file descriptors per worker, and preserves ABI compatibility with older `fuse_session_loop_mt` signatures.

## Important APIs, Types, And Functions

Private runtime types are `struct fuse_worker`, which stores list links, pthread id, per-thread `fuse_buf`, optional cloned `fuse_chan`, and parent `fuse_mt`; and `struct fuse_mt`, which stores worker counts, available-worker count, session pointer, sentinel list node, error, clone-fd flag, idle-thread cap, and max-thread cap.

Channel APIs implemented here are `fuse_chan_get` and `fuse_chan_put`, backed by private `fuse_chan_new`. Thread creation is centralized in `fuse_start_thread`, which also applies `FUSE_THREAD_STACK` and blocks termination-related signals in worker threads during `pthread_create`.

Loop entry points are `fuse_session_loop_mt_312`, `fuse_session_loop_mt_32`, and `fuse_session_loop_mt_31`, exported with symbol versions for FUSE 3.12, 3.2, and 3.0 compatibility. Loop-config APIs are `fuse_loop_cfg_create`, `fuse_loop_cfg_destroy`, `fuse_loop_cfg_verify`, `fuse_loop_cfg_convert`, `fuse_loop_cfg_set_idle_threads`, `fuse_loop_cfg_set_max_threads`, and `fuse_loop_cfg_set_clone_fd`.

## Control Flow

`fuse_session_loop_mt_312` verifies or creates a config, initializes `struct fuse_mt`, starts the first worker while holding `se->mt_lock`, then waits on `se->mt_finish` until `fuse_session_exited(se)` is true. When the session exits, it cancels all workers, joins them through `fuse_join_worker`, records `mt.error`, stops io_uring if present, applies `se->error` override, destroys an auto-created config, and returns.

Each worker runs `fuse_do_work`. It enables cancellation around `fuse_session_receive_buf_internal`, retries `-EINTR`, exits on nonpositive results, and on negative receive errors marks the session exited and records `mt->error`. For a valid request, it locks `se->mt_lock`, detects `FUSE_FORGET` and `FUSE_BATCH_FORGET` requests as a special no-scale-up case, decrements available worker count for non-forget work, and starts another worker when no workers are available, `numworker < max_threads`, and the session has received init. It then processes the buffer with `fuse_session_process_buf_internal` and restores availability.

Idle worker reaping occurs after processing when `max_idle != -1`, available workers exceed the configured idle cap, and more than one worker exists. The worker removes itself from the list, decrements counts, detaches itself, frees its buffer, drops its channel, and exits.

Clone-fd flow starts in `fuse_loop_start_thread`. If `clone_fd` is enabled, it calls `fuse_clone_chan`, which uses either custom `se->io->clone_fd` or `fuse_clone_chan_fd_default`. The default path opens `/dev/fuse`, sets close-on-exec if needed, and issues `FUSE_DEV_IOC_CLONE` with the session master fd. If cloning fails once, the loop logs and disables further clone-fd attempts.

Compatibility entry points allocate a new private config and convert older inputs. `fuse_loop_cfg_convert` maps v1 `max_idle_threads` to both `max_threads` and `max_idle_threads` to preserve older pool-cap behavior, then transfers `clone_fd`.

## State And Persistence Behavior

State is runtime-only. Worker list membership, `numworker`, `numavail`, `mt.error`, session exit state, and the per-worker buffers/channels are mutated under `se->mt_lock` except for receive/process work outside the lock. `se->mt_finish` is a semaphore used to wake the controller when workers leave the receive loop.

Channels own cloned fds and close them when their reference count reaches zero. Worker buffers are retained per worker so cancellation cleanup can free memory correctly. The environment variable `FUSE_THREAD_STACK` influences pthread stack size but is not persisted.

## Dependencies And Integration Points

The file includes low-level, kernel, misc, io_uring, util, and internal headers. It depends on pthreads, signals, semaphores, ioctl, `/dev/fuse`, `FUSE_DEV_IOC_CLONE`, `fcntl`, and close-on-exec behavior. It integrates with `struct fuse_session` fields declared in `fuse_i.h`, especially `mt_lock`, `mt_finish`, `got_init`, `error`, `io`, `fd`, and `uring.pool`.

High-level `fuse_loop_mt_312` in `fuse.c` calls this session loop after starting the high-level cleanup thread. Low-level users can call the session loop directly.

## Risks And Edge Cases

The worker-scaling algorithm intentionally ignores FORGET bursts when deciding to spawn more threads. This prevents thread explosions but can delay scaling if mixed workloads are misclassified or if buffers are fd-backed and opcode inspection is unavailable.

`max_threads` can be set to zero by the public setter even though the worker-spawn condition requires `numworker < max_threads`; because the first worker is started before demand scaling, zero effectively prevents additional workers after the initial one. Invalid extremely large idle-thread values are rejected in `fuse_loop_cfg_set_idle_threads`, but `fuse_loop_cfg_set_max_threads` does not cap against `FUSE_LOOP_MT_MAX_THREADS`.

Thread cancellation is used for shutdown. Correct cleanup relies on cancellation being enabled only during receive and disabled around processing and list manipulation. If a worker exits through the idle-reap branch it detaches itself and frees its own structure, so list/count locking must remain correct.

`fuse_chan_get` asserts `ch->ctr > 0` before locking, which is not a synchronization guarantee by itself. Callers need a valid channel reference before calling it. Clone-fd fallback logs an error and continues without clone-fd, which may hide a performance or isolation regression unless tests assert the fallback path.

## Test Signals

Tests should cover config creation defaults, version-id verification, v1 conversion semantics, setter warnings and edge values, custom and default clone-fd success/failure, environment-controlled thread stack parsing, signal mask restoration after thread creation, worker growth up to `max_threads`, no growth on FORGET-only bursts, idle worker reaping, receive errors setting session exit and return errors, cancellation and join cleanup, channel reference-count close behavior, and io_uring stop on exit.
