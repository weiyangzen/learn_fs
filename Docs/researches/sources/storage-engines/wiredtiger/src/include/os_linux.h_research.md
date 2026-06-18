# sources/storage-engines/wiredtiger/src/include/os_linux.h

## Purpose
Provides Linux-specific semaphore typedefs for the WiredTiger OS abstraction.

## Important APIs, Types, And Functions
- Includes `<semaphore.h>`.
- Defines `wt_sem_t` as `sem_t`.

## Control Flow
No executable logic is defined here. Common semaphore code uses the platform typedef.

## State And Persistence Behavior
Semaphore state is runtime synchronization state only.

## Dependencies And Integration Points
Integrated by platform selection and `WT_SEMAPHORE` in `mutex.h`. It must match Linux semaphore initialization, wait/post, and destroy implementations.

## Risks
Linux uses POSIX semaphores while Darwin uses dispatch semaphores and Windows uses handles. Cross-platform semaphore code must not assume a shared representation.

## Test Signals
Linux CI should run semaphore wait/post/timeout tests and thread-group signaling paths that use `wt_sem_t`.
