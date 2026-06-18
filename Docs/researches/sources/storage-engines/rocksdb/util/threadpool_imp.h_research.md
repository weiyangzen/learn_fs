# sources/storage-engines/rocksdb/util/threadpool_imp.h

## Purpose

Declares `ThreadPoolImpl`, the concrete `ThreadPool` implementation backing RocksDB background execution.

## APIs, control flow, and state

The class implements thread joining, background thread sizing, queue length, job submission, schedule/unschedule by tag, priority changes, Env association, thread priority, and reserve/release of idle threads. It exposes `PthreadCall` for checked pthread return handling and hides implementation details behind `std::unique_ptr<Impl>`.

## Dependencies and integration

It depends on `rocksdb/env.h` and `rocksdb/threadpool.h`. Env priority pools call into this implementation for HIGH/LOW/BOTTOM/USER background work.

## Risks and test signals

The header's pimpl boundary keeps ABI-facing declarations small but means most behavior is in `threadpool_imp.cc`. API risks include distinction between `JoinAllThreads` discarding queued jobs and `WaitForJobsAndJoinAllThreads` draining them, and `Schedule` being the only API with unschedule callbacks.
