# sources/storage-engines/wiredtiger/src/os_darwin/os_mtx_sem.c

## Purpose
Provides Darwin semaphore primitives for WiredTiger using Grand Central Dispatch semaphores.

## Important APIs, Types, and Functions
Functions are `__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait`. `WT_SEMAPHORE` stores a name and dispatch semaphore object.

## Control Flow
Initialization creates a dispatch semaphore with count zero, then signals it `count` times because creation does not accept a nonzero initial count. Post signals the semaphore and ignores the wake-status return. Wait blocks forever with `DISPATCH_TIME_FOREVER`. Destroy releases the dispatch object and clears the struct.

## State and Persistence Behavior
Semaphore state is in memory and kernel/dispatch runtime state. There is no persistence.

## Dependencies and Integration Points
This file backs WiredTiger's platform semaphore abstraction on Darwin for worker threads and synchronization primitives.

## Risks and Edge Cases
Initialization loops once per initial count, so very large initial counts are inefficient. Wait should not time out, so any nonzero dispatch return is treated as `EINVAL`. Destroy assumes a valid initialized dispatch object.

## Test Signals
Thread synchronization tests on Darwin should cover initial counts, post/wait ordering, blocking wakeup, destroy after use, and failure injection for semaphore creation.
