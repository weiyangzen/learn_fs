# sources/storage-engines/rocksdb/util/single_thread_executor.h

## Purpose

Provides a coroutine-only `folly::Executor` that runs callbacks synchronously on the current thread while polling an `AsyncFileReader` when the local queue becomes idle.

## APIs, control flow, and state

When `USE_COROUTINES` is enabled, `SingleThreadExecutor::add` pushes the callback into `q_`. If this callback made the queue transition from empty to non-empty and the executor is not in the busy guard, it drains the queue in a tight loop. After each drain to empty, it sets `busy_`, calls `reader_.Wait()` so async I/O completions can resume coroutines and enqueue more work, then clears `busy_`.

## Dependencies and integration

The class depends on Folly executor APIs and `util/async_file_reader.h`. It integrates with coroutine code paths that need same-thread resumption rather than dispatch to a CPU pool.

## Risks and test signals

There is no direct test in this subset. It is not a general thread-safe executor: `q_` and `busy_` are plain state. Correctness relies on the comment guarantee that async I/O completion callbacks are not scheduled onto the same executor/thread in a way that deadlocks.
