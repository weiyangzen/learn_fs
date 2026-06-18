# sources/test-tools/fio/filelock.c

## Purpose
`filelock.c` implements simple process-local exclusive locks keyed by filename hash. It lets fio coordinate access to the same file among job threads without using OS file locks.

## Important APIs, Types, And Functions
`struct fio_filelock` holds a filename hash, a semaphore used as the per-file lock, list linkage, and reference count. Global `struct filelock_data` owns an active list, global semaphore, free list, and fixed pool of `MAX_FILELOCKS` lock objects. Public APIs are `fio_filelock_init`, `fio_filelock_exit`, `fio_lock_file`, `fio_trylock_file`, and `fio_unlock_file`.

## Control Flow
Initialization allocates the global pool, initializes global/per-lock semaphores, and puts all locks on the free list. `__fio_lock_file()` hashes the filename, finds or allocates a lock object under the global lock, increments references, then either blocks on the per-file semaphore or attempts trylock-specific race handling. `fio_unlock_file()` hashes again, finds the active lock, decrements references, releases the per-file semaphore, and returns the object to the free list when references reach zero. Blocking allocation waits by dropping the global lock, sleeping, and retrying when the fixed pool is exhausted.

## State And Persistence
All state is process-local and stored in the fixed smalloc pool. Locks are keyed only by 32-bit hash, not full filename strings, so collisions alias. No OS-level persistence exists.

## Dependencies And Integration Points
The code depends on fio intrusive lists, semaphores, `smalloc`, Jenkins hash, logging, and `lib/types.h` via the header. File setup/locking code uses this as a shared synchronization primitive.

## Risks
Hash collisions can serialize unrelated files or incorrectly make trylock fail. The trylock path returns `true` when no free lock object is available, which semantically means "could not lock" but can be easy to misread. `fio_filelock_exit()` asserts the active list is empty, so teardown with leaked locks aborts in assert builds. The fixed `MAX_FILELOCKS` pool can throttle large jobs.

## Test Signals
Tests should cover blocking lock/unlock, trylock success/failure, reference counts with multiple lockers, pool exhaustion behavior, hash collision behavior via injected hashes if possible, and exit assertions/cleanup after all locks are released.
