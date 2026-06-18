# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/MutexPoolLock.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 45 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `LockName`, `MutexPoolLock`. Macros/constants: `MESSMER_CPPUTILS_LOCK_MUTEXPOOLLOCK_H`. Important declarations or call sites include `MutexPoolLock(LockPool<LockName> *pool, const LockName &lockName): _pool(pool), _lockName(lockName) {`; `_pool->lock(_lockName);`; `: _pool(pool), _lockName(lockName) {`; `_pool->lock(_lockName, lockToFreeWhileWaiting);`; `MutexPoolLock(MutexPoolLock &&rhs) noexcept: _pool(rhs._pool), _lockName(std::move(rhs._lockName)) {`; `~MutexPoolLock() {`; `if (_pool != nullptr) {`; `unlock();`; `void unlock() {`; `ASSERT(_pool != nullptr, "MutexPoolLock is not locked");`. CMake commands used here include `MutexPoolLock`, `if`, `unlock`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `LockPool.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `LockPool.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.
