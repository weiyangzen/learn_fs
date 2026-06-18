# sources/user-network-fs/libnfs/lib/multithreading.c

## Purpose

`multithreading.c` provides the optional platform abstraction used when libnfs is built with `HAVE_MULTITHREADING`. It starts and stops the background NFS service thread, identifies the current thread, and wraps mutex and semaphore primitives for Windows, pthread platforms, Apple dispatch semaphores, and POSIX semaphores. The synchronous API uses these primitives to let multiple caller threads issue blocking operations while one service thread drives the shared RPC socket.

## Important APIs, Types, and Functions

The exported helpers are `nfs_mt_get_tid`, `nfs_mt_service_thread_start`, `nfs_mt_service_thread_stop`, `nfs_mt_mutex_init`, `nfs_mt_mutex_destroy`, `nfs_mt_mutex_lock`, `nfs_mt_mutex_unlock`, `nfs_mt_sem_init`, `nfs_mt_sem_destroy`, `nfs_mt_sem_post`, and `nfs_mt_sem_wait`. The internal service routine is `nfs_mt_service_thread`, with a Windows `service_thread_init` adapter for `CreateThread`.

On Windows, thread IDs come from `GetCurrentThreadId`, mutexes and semaphores are implemented with `CreateSemaphoreA`, waits use `WaitForSingleObject`, and the service thread is a Win32 thread handle stored in `nfs->nfsi->service_thread`. On pthread platforms, thread IDs use the best available OS mechanism (`pthread_threadid_np`, `pthread_getthreadid_np`, `getthrid`, `_lwp_self`, or `syscall(SYS_gettid)`). Mutexes are pthread mutexes, with `PTHREAD_MUTEX_ERRORCHECK` enabled under `DEBUG_PTHREAD_LOCKING_VIOLATIONS`. Semaphores use dispatch semaphores on Apple when available or `sem_init`/`sem_wait` elsewhere.

## Control Flow

Starting the service thread creates the platform thread with the `nfs_context` as its argument, then spins until `rpc->multithreading_enabled` becomes nonzero. The service thread sets that flag, then loops while it remains true. Each loop builds a `pollfd` from `nfs_get_fd` and `nfs_which_events`, polls with the RPC poll timeout on pthread platforms or a zero timeout on Windows, maps poll failures to `revents = -1`, and calls `nfs_service` to process socket events. Stop clears `rpc->multithreading_enabled` and joins or waits for the thread to exit.

Mutex and semaphore functions are thin wrappers, so higher layers can use `libnfs_mutex_t` and `libnfs_sem_t` without preprocessor-heavy call sites. In the synchronous facade, each blocking operation initializes a semaphore with value zero and waits for its callback to post; shared structures such as RPC queues, directory cache, and thread-context lists use the mutex wrappers.

## State and Persistence Behavior

The file stores no independent persistent state. It mutates `nfs->rpc->multithreading_enabled` as the service thread run flag and uses `nfs->nfsi->service_thread` to hold the platform thread handle or pthread ID. Mutex and semaphore state lives in caller-owned objects embedded in RPC/NFS contexts or callback data. All state is process-local and must be destroyed by context teardown or per-call cleanup.

## Dependencies and Integration Points

This file depends on `libnfs.h`, `libnfs-raw.h`, `libnfs-private.h`, `poll`, and platform threading APIs. It is used by `libnfs-sync.c` for semaphore-based synchronous waits, by `libnfs.c` for directory cache and error locking, and by lower RPC/PDU/socket/init code for queue and error synchronization. Its API surface is compiled out entirely when `HAVE_MULTITHREADING` is not defined.

## Risks and Edge Cases

The run flag is a plain integer shared between threads; correctness relies on platform memory behavior around thread creation, polling, and join rather than explicit atomics. `nfs_mt_service_thread_start` busy-waits until the service thread sets the flag, so thread startup failure after creation could spin. The Windows service loop polls with timeout zero, which can consume CPU if no socket events are available. Windows `nfs_mt_sem_init` ignores the requested initial value and always creates the semaphore with count zero, which matches current sync-call use but is not a general semaphore implementation.

Pthread builds require one of the supported thread ID APIs; otherwise compilation fails with `#error`. Error-checking mutex initialization may leak the mutex attribute object because it is not destroyed after `pthread_mutex_init`. Semaphore waits do not retry on `EINTR`, so POSIX `sem_wait` interruption can propagate as failure if callers ever inspect the return code. Service-thread shutdown can block indefinitely if `nfs_service` or `poll` does not return.

## Test Signals

Tests should build all supported threading variants where possible: Windows, pthread/Linux, BSD/macOS thread ID paths, Apple dispatch semaphore, POSIX semaphore, and no-multithreading. Runtime tests should start the service thread, issue simultaneous synchronous operations from multiple threads, verify per-thread callback wakeups, exercise mutex-protected directory cache and error paths, and stop the service thread cleanly while no operations are pending. Fault tests should simulate poll errors, service errors, semaphore wait/post failures where injectable, interrupted waits, and rapid start/stop cycles.
