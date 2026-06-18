# sources/storage-engines/rocksdb/util/repeatable_thread.h

## Purpose
Defines `RepeatableThread`, a small wrapper around `port::Thread` that repeatedly invokes a callback after an initial delay and then at a fixed microsecond interval until cancelled.

## Important APIs, Types, And Functions
The constructor takes a function, thread name suffix, `SystemClock*`, delay, and optional initial delay, then starts the thread. `cancel` stops the loop, wakes the condition variable, and joins the thread. `IsRunning` returns the running flag. In debug builds, `TEST_WaitForRun` lets tests wait until the worker is sleeping, run a callback such as clock advancement, then wait for one callback execution.

## Control Flow
The thread sets a platform thread name where supported, waits for the initial delay, then repeatedly runs `function_` and calls `wait(delay_us_)`. `wait` holds an `InstrumentedMutex`, computes an absolute wake time from `clock_->NowMicros()`, performs timed waits until time has advanced enough or cancellation occurs, and returns whether the loop should continue. Cancellation flips `running_` under the mutex and signals all waiters before joining.

## State And Persistence
Stores callback, thread name, raw clock pointer, delays, instrumented mutex/condition variable, running flag, and debug-only waiting/run counters. There is no persistence; lifetime is tied to the object and destructor cancels automatically.

## Dependencies And Integration Points
Depends on RocksDB instrumented mutex/condition-variable types, `port::Thread`, `SystemClock`, and scoped locks. It integrates with background maintenance tasks that need periodic callbacks, and tests can use mock clocks through `TEST_WaitForRun`.

## Risks
`IsRunning` reads `running_` without locking, which can be a data race if called concurrently with `cancel`. The constructor asserts `delay_us_ > 0` in the thread body despite the class comment saying zero means repeated calls without delay; this mismatch is a behavioral risk. `clock_` is a raw pointer and must outlive the thread. `function_` exceptions are not handled. `cancel` must not be called from the repeatable thread itself because it joins.

## Test Signals
`repeatable_thread_test.cc` validates real-time periodic execution and cancellation, plus deterministic mock-clock execution with debug-only `TEST_WaitForRun`. A macOS debug workaround uses sync points to avoid immediate timed-wait return causing hangs.
