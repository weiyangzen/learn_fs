# sources/storage-engines/rocksdb/util/stop_watch.h

## Purpose

Provides scoped timing helpers for RocksDB statistics and elapsed-time accounting in microseconds or nanoseconds.

## APIs, control flow, and state

`StopWatch` captures `start_time_` when statistics or elapsed output are needed. On destruction it writes or adds elapsed microseconds, optionally subtracts tracked delay, and reports to one or two enabled histograms when statistics level permits timers. `DelayStart`/`DelayStop` accumulate excluded time only when an elapsed pointer and delay tracking are enabled. `StopWatchNano` measures wall-clock or CPU nanoseconds, supports manual or automatic start, optional reset on elapsed read, null-safe elapsed reads, and microsecond conversion.

## Dependencies and integration

It depends on `monitoring/statistics_impl.h` and `rocksdb/system_clock.h`. It integrates with RocksDB perf/statistics sites through histogram IDs and `SystemClock`.

## Risks and test signals

There are no direct tests here. Risks include passing invalid histogram IDs, elapsed subtraction under repeated delay calls, and using `ElapsedNanos` before `Start`. The implementation avoids timer overhead when both stats and elapsed output are disabled.
