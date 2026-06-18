# sources/storage-engines/foundationdb/fdbserver/workloads/SlowTaskWorkload.cpp

## Purpose
`SlowTaskWorkload` stress-tests the slow task profiler or Flow profiler by repeatedly doing expensive exception unwinding in a tight loop while profiling is enabled.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `SlowTaskWorkload`. The important methods are `start`, static actor `go`, and non-actor helper `do_slow_exception_thing`. It uses `setupRunLoopProfiler`, `SignalSafeUnwind` counters, `dl_iterate_phdr_calls`, and `fmt::print`.

## Control Flow
`start` enables the run loop profiler and returns `go`. `go` waits one second, snapshots profiler counters, then for ten one-second intervals repeatedly calls `do_slow_exception_thing`, which throws and catches `success()` one thousand times per call. At completion it prints exception and profiler counter deltas to stderr.

## State And Persistence Behavior
There is no database state. The workload mutates profiler/runtime counters and produces stderr output.

## Dependencies And Integration Points
It depends on Flow profiling and signal-safe unwind infrastructure. The helper is deliberately non-actor so actual exception unwinding occurs, making it a runtime/profiler stressor rather than a database workload.

## Risks And Edge Cases
This workload intentionally burns CPU and throws large numbers of exceptions. It can perturb timing-sensitive simulations and should be used only where slow-task profiling behavior is the target.

## Test Signals
The printed summary reports exception count, `dl_iterate_phdr` call delta, profiles disabled, profiles overflowed, and profiles captured. `check` always returns true.
