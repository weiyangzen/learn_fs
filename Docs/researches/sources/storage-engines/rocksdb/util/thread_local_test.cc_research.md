# sources/storage-engines/rocksdb/util/thread_local_test.cc

## Purpose

Validates `ThreadLocalPtr` id allocation, per-thread isolation, cleanup semantics, aggregate operations, and atomic pointer operations.

## APIs, control flow, and state

`UniqueIdTest` checks monotonic id assignment and LIFO recycling. `SequentialReadWriteTest` repeatedly starts threads to ensure values do not leak between thread lifetimes. `ConcurrentReadWriteTest` runs reader and writer groups using two `ThreadLocalPtr` instances and distinct per-thread values. `Unref` covers no-access, thread-exit cleanup, and instance-destruction cleanup. `Scrape` removes values across live threads without later unrefs. `Fold` sums per-thread atomic counters. `CompareAndSwap` and `Swap` test atomic slot operations.

## Dependencies and integration

It uses Env thread launching, port mutex/condition variables, sync points, and autovector. The tests exercise real thread exit handlers through `Env::WaitForJoin`.

## Risks and test signals

The strongest signals are exact unref counts and per-thread value isolation under concurrent access. The disabled `MainThreadDiesFirst` case documents a lifetime hazard that requires manual ASAN-oriented validation rather than normal automated execution.
