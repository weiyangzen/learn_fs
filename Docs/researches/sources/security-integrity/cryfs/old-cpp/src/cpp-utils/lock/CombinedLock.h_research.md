# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/CombinedLock.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 37 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `is`, `CombinedLock`. Macros/constants: `MESSMER_CPPUTILS_LOCK_COMBINEDLOCK_H`. Important declarations or call sites include `: _outer(outer), _inner(inner) {`; `void lock() {`; `_outer->lock();`; `_inner->lock();`; `void unlock() {`; `_inner->unlock();`; `_outer->unlock();`; `DISALLOW_COPY_AND_ASSIGN(CombinedLock);`. CMake commands used here include `CombinedLock`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `../macros.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `../macros.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.
