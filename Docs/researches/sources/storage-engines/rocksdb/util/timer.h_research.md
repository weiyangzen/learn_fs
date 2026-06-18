# sources/storage-engines/rocksdb/util/timer.h

## Purpose

Defines `Timer`, a single-thread repeated-work scheduler keyed by unique function names and driven by `SystemClock` microsecond time.

## APIs, control flow, and state

`Add` creates a `FunctionInfo`, assigns `next_run_time_us` under lock, rejects duplicate names and tasks scheduled before a currently executing task, inserts into both heap and map, and signals the worker. `Start` creates the timer thread if not already running. `Run` waits on an empty heap or until the earliest task is due, skips invalidated tasks, copies and executes due functions outside the mutex, then either reschedules by setting next run to completion time plus repeat interval or erases the task. `Cancel` invalidates by name and waits if that task is executing. `Shutdown` cancels all work, wakes, joins, and is also called by the destructor.

## Dependencies and integration

It depends on `InstrumentedMutex`, `InstrumentedCondVar`, `SystemClock`, `port::Thread`, and sync points for deterministic tests. It is appropriate for lightweight repeated housekeeping, not long-running work.

## Risks and test signals

`Start` and `Shutdown` are explicitly not thread-safe with each other. Tasks execute serially, so long functions delay later work. `timer_test.cc` covers one-shot, repeated, multiple tasks, add-after-start, duplicate rejection, cancel/shutdown while running, repeat interval after function runtime, and destructor shutdown with a mock clock.
