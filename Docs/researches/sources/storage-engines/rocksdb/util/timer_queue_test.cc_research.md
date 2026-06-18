# sources/storage-engines/rocksdb/util/timer_queue_test.cc

## Purpose

Smoke-tests `TimerQueue` construction and scheduling of one-shot and repeating handlers.

## APIs, control flow, and state

The test creates a queue, records a local start time, adds two long one-shot timers, one repeating 1-second timer, and one repeating 2-second timer. Handlers print elapsed time and return reschedule decisions based on whether they were aborted. The cancel calls are present only as comments.

## Dependencies and integration

It depends on `util/timer_queue.h`, futures indirectly through included headers, and the RocksDB test harness. Queue destruction at test end triggers shutdown and cancellation of pending work.

## Risks and test signals

The only automated assertion is `ASSERT_TRUE(true)`, so this mainly detects crashes during add/destruction. It does not verify timing, cancellation counts, abort flags, repeat behavior, or worker-thread affinity.
