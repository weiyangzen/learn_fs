# sources/storage-engines/rocksdb/util/work_queue.h

## Purpose

Defines a generic thread-safe FIFO work queue with optional bounded capacity and an explicit finish signal.

## APIs, control flow, and state

`push` waits while the queue is full and not done, returns false if `finish` has been called, otherwise enqueues and wakes one reader. `pop` waits while empty and not done, returns false without modifying the output once empty and finished, otherwise pops FIFO and wakes one writer. `setMaxSize` changes the bound and wakes writers. `finish` sets `done_`, asserts it was not already done, and wakes readers, writers, and finish waiters. `waitUntilFinished` blocks until `done_` is true.

## Dependencies and integration

The header uses standard mutexes, condition variables, and `std::queue`. It is imported from Facebook's zstd pzstd utility and namespaced into RocksDB.

## Risks and test signals

The queue is single-finish only and unbounded when `maxSize_ == 0`. Bounded producers can be released by `finish` without pushing. `work_queue_test.cc` covers single-thread, SPSC, SPMC, MPMC, bounded behavior, changing max size, failed push after finish, and failed pop preserving the output value.
