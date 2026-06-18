# sources/storage-engines/wiredtiger/src/os_linux/os_mtx_sem.c

## Purpose
Provides Linux/POSIX semaphore primitives for WiredTiger using unnamed POSIX semaphores.

## Important APIs, Types, and Functions
Functions are `__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait`.

## Control Flow
Initialization clears the struct, stores the name, and calls `sem_init` with process-local sharing and the requested count. Destroy calls `sem_destroy` and clears the struct. Post calls `sem_post`. Wait loops on `sem_wait`, retrying `EINTR` and returning other errno values.

## State and Persistence Behavior
Semaphore state is in memory and kernel/libpthread state only. There is no persistence.

## Dependencies and Integration Points
This is the Linux semaphore backend for WiredTiger thread coordination, used by background services and synchronization abstractions.

## Risks and Edge Cases
`sem_wait` interruption is handled, but other errors surface directly. Destroying a semaphore with waiters or after failed init is a caller bug. The name is stored for diagnostics but not used by POSIX semaphores.

## Test Signals
Linux thread tests should cover initial count behavior, post/wait, signal interruption, destroy, and concurrent producers/consumers.
