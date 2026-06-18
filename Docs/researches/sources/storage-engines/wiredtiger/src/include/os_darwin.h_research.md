# sources/storage-engines/wiredtiger/src/include/os_darwin.h

## Purpose
Provides Darwin-specific semaphore typedefs for the WiredTiger OS abstraction.

## Important APIs, Types, And Functions
- Includes `<dispatch/dispatch.h>`.
- Defines `wt_sem_t` as `dispatch_semaphore_t`.

## Control Flow
No executable logic is defined here. Platform-specific semaphore implementation code uses `wt_sem_t` through common names.

## State And Persistence Behavior
Semaphore state is in-memory kernel/runtime synchronization state only.

## Dependencies And Integration Points
Integrated by platform selection headers and semaphore code in the OS layer. Must be consistent with `mutex.h`'s `WT_SEMAPHORE` wrapper.

## Risks
Darwin semaphore lifecycle must use dispatch semaphore APIs, not POSIX `sem_t` calls. Type mismatches would surface at compile time or during semaphore initialization/destruction.

## Test Signals
Darwin builds should compile semaphore code and run thread signaling tests covering wait, post, timeout, and destruction.
