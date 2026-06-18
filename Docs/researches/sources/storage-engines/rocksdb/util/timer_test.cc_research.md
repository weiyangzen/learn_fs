# sources/storage-engines/rocksdb/util/timer_test.cc

## Purpose

Provides deterministic unit tests for `Timer` scheduling, repetition, cancellation, shutdown, duplicate names, and destructor behavior.

## APIs, control flow, and state

The fixture uses `MockSystemClock` and installs timed-wait fixes. Tests add one or more functions, start the timer, advance mock time with `TEST_WaitForRun`, and inspect counters. SyncPoint dependencies coordinate cancellation, shutdown, or deletion while a task is running. Duplicate-name tests assert the second `Add` fails. Repeat interval tests confirm the interval is measured from task completion, not task start.

## Dependencies and integration

It depends on `util/timer.h`, `db/db_test_util.h`, and `test_util/mock_time_env.h`. The tests exercise real timer threads but deterministic clock advancement.

## Risks and test signals

Signals cover pending task rescheduling, task cancellation waiting for running functions, shutdown waiting for running functions, deletion safety, and single-thread task ordering. The suite does not cover concurrent `Start`/`Shutdown`, which the class explicitly does not support.
