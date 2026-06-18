# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 91 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `LockName`, `LockPool`, `OuterLock`. Macros/constants: `MESSMER_CPPUTILS_LOCK_LOCKPOOL_H`. Important declarations or call sites include `LockPool();`; `~LockPool();`; `void lock(const LockName &lockName);`; `void lock(const LockName &lockName, std::unique_lock<std::mutex> *lockToFreeWhileWaiting);`; `void release(const LockName &lockName);`; `bool _isLocked(const LockName &lockName) const;`; `template<class OuterLock> void _lock(const LockName &lockName, OuterLock *lockToFreeWhileWaiting);`; `DISALLOW_COPY_AND_ASSIGN(LockPool);`; `inline LockPool<LockName>::LockPool(): _lockedLocks(), _mutex(), _cv() {}`; `inline LockPool<LockName>::~LockPool() {`. CMake commands used here include `LockPool`, `DISALLOW_COPY_AND_ASSIGN`, `ASSERT`, `_lock`, `if`. Primary includes/dependencies visible in the file include `mutex`, `condition_variable`, `vector`, `algorithm`, `../assert/assert.h`, `../macros.h`, `CombinedLock.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `mutex`, `condition_variable`, `vector`, `algorithm`, `../assert/assert.h`, `../macros.h`, `CombinedLock.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.
