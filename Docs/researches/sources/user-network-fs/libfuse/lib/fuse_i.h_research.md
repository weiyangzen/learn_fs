# sources/user-network-fs/libfuse/lib/fuse_i.h

## Purpose

`fuse_i.h` is a central private libfuse header that defines internal request, session, channel, module, and loop-configuration structures shared across the library implementation. It bridges public headers such as `fuse.h` and `fuse_lowlevel.h` with implementation files such as `fuse.c`, `fuse_lowlevel.c`, `fuse_loop.c`, `fuse_loop_mt.c`, mount backends, buffer utilities, and daemonization code.

## Important APIs, Types, And Functions

Key internal structures are `struct fuse_req`, `struct fuse_notify_req`, `struct fuse_session_uring`, `struct fuse_session`, `struct fuse_chan`, `struct fuse_module`, and, for API versions at or above 3.12, the private `struct fuse_loop_config`.

`struct fuse_req` stores the owning session, unique request id, atomic reference count, request lock, credentials/context, channel, interruption state, io_uring/copy-file-range flags, interrupt callback union, list links, and security-context iterator state. `struct fuse_session` stores mountpoint, fd/custom I/O, mount options, low-level ops, userdata, owner, connection info, request and interrupt lists, locks, initialization and destroy state, thread-loop synchronization, buffer sizing, synchronous FUSE_INIT state, io_uring pool settings, timeout thread pointer, and desired connection feature masks.

`struct fuse_chan` is a reference-counted wrapper around a FUSE device fd used by clone-fd multithreaded loops. `struct fuse_module` tracks high-level stack modules, their factories, dynamic-library ownership, and reference counts. `struct fuse_loop_config` is the ABI-safe internal v2 loop configuration with a `version_id`, `clone_fd`, `max_idle_threads`, and `max_threads`.

Function declarations cover channel reference management, mount backend calls, reply sending and request freeing, CUSE initialization, thread creation, buffer freeing, internal receive/process functions, high-level constructor and multithread loop ABI entry points, loop config verification, and daemonization-state detection.

## Control Flow

This header has no executable control flow, but it defines the shared data model used by the core control paths. Session loops receive requests into `struct fuse_buf`, associate them with `struct fuse_req`, and process them through `fuse_session_process_buf_internal`. Multithreaded loops create and release `struct fuse_chan` instances when clone-fd mode is enabled. High-level creation in `fuse.c` calls `fuse_session_new_versioned` and relies on `struct fuse_session` fields for synchronization and errors.

The private loop config uses `version_id` to distinguish the newer internal layout from the older public `struct fuse_loop_config_v1`, whose first field overlapped with `clone_fd`. `fuse_loop_cfg_verify` enforces this before `fuse_session_loop_mt_312` consumes the structure.

## State And Persistence Behavior

All structures describe in-memory runtime state. There is no disk persistence. State with broad behavioral impact includes request reference counts, session exit/error flags, `got_init`, feature masks, buffer size, multithread exit semaphore/lock, sync-init wakeup fields, io_uring pool pointer, timeout thread pointer, module reference counts, and channel fd reference counts.

The `mountpoint` and `bufsize` fields are atomic because they can be read or updated across session-management paths. `mt_exited`, `uring.pool`, and `timeout_thread` coordinate asynchronous loop and teardown behavior across threads.

## Dependencies And Integration Points

The header includes `fuse.h`, `fuse_lowlevel.h`, and `util.h`, plus pthreads, semaphores, atomics, fixed-width integers, and booleans. It is included by the session loops, high-level API implementation, low-level implementation, mount code, CUSE code, buffer code, io_uring support, and daemonization integration.

It also defines constants `FUSE_DEFAULT_MAX_PAGES_LIMIT`, `FUSE_DEFAULT_MAX_PAGES_PER_REQ`, and `FUSE_BUFFER_HEADER_SIZE`, which influence buffer sizing and kernel request capacity assumptions.

## Risks And Edge Cases

As a private ABI coordination header, layout changes can break implementation files that access fields directly. `struct fuse_session` is especially sensitive because it combines mount state, request queues, synchronization primitives, feature negotiation, io_uring state, and sync-init state. The private `struct fuse_loop_config` is guarded by `version_id`; callers passing an older public layout to the new API should receive `-EINVAL` instead of being misinterpreted.

`MIN` is defined as a GNU statement-expression macro using `typeof`, so this private header assumes GNU C extensions. Channel `ctr` updates depend on callers holding `struct fuse_chan.lock` as implemented in `fuse_loop_mt.c`; misuse outside those helpers could race with fd close and free.

## Test Signals

Compile-time tests should cover supported `FUSE_USE_VERSION` boundaries, especially the visibility and compatibility of `struct fuse_loop_config` versus `struct fuse_loop_config_v1`. Runtime tests should exercise request reference counting, channel get/put close behavior, session receive/process behavior with and without custom I/O, sync-init fields, io_uring shutdown interactions, and multithread loop config validation.
