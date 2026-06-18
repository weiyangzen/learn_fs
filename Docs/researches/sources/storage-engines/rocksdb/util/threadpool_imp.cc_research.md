# sources/storage-engines/rocksdb/util/threadpool_imp.cc

## Purpose

Implements RocksDB's default `ThreadPool` with dynamic thread counts, queued jobs, unscheduling, reservations, priority lowering, thread-status registration, and shutdown modes.

## APIs, control flow, and state

The `Impl` pimpl stores queue state, thread vector, total thread limit, waiting/reserved counters, exit flags, Env priority, low-IO and CPU-priority settings, and an atomic queue length. `Submit` starts threads as needed, enqueues a `BGItem`, updates queue length, and wakes workers. Each `BGThread` waits while the queue is empty, the thread is excessive, or reservations consume available waiting threads. It exits on shutdown, detaches and removes last excessive threads when limits shrink, pops work, applies lower priorities if requested, and runs the job outside the mutex. `JoinThreads(false)` discards queued work; `JoinThreads(true)` drains it. `UnSchedule` removes matching queued tags and runs unschedule callbacks outside the mutex.

## Dependencies and integration

It depends on Env/threadpool APIs, `monitoring/thread_status_util.h`, port thread/priority primitives, sync points, and `errnoStr`. `NewThreadPool` constructs and sizes an instance for Env background pools.

## Risks and test signals

Risks cluster around concurrency: reserved-thread accounting, shrinking pools by detaching workers, queue length relaxed atomics, and jobs submitted during shutdown. `thread_list_test.cc` indirectly exercises background scheduling, reservations, and thread status, but there is no direct comprehensive threadpool test in this subset.
