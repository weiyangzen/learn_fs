# sources/storage-engines/rocksdb/util/thread_local.h

## Purpose

Declares `ThreadLocalPtr`, a pointer-only thread-local abstraction that separates values by both current thread and `ThreadLocalPtr` instance.

## APIs, control flow, and state

The class exposes `Get`, `Reset`, `Swap`, `CompareAndSwap`, `Scrape`, and `Fold`. It accepts an optional `UnrefHandler` invoked for non-null stored pointers when a thread terminates or the `ThreadLocalPtr` instance is destroyed. `TEST_PeekId` exposes the next allocator id for tests, and `InitSingletons` forces static singleton construction.

## Dependencies and integration

The header depends on atomics, functions, unordered maps, `port/port.h`, and `util/autovector.h`. It is intended for object-scoped thread-local storage in DB components, avoiding collisions that plain `thread_local` members would create across DB instances.

## Risks and test signals

The header documents the largest risk: unref handlers run under a global mutex shared by most methods, so callback implementations can deadlock if they lock or call back into `ThreadLocalPtr`. `thread_local_test.cc` exercises the public API and cleanup lifecycle.
