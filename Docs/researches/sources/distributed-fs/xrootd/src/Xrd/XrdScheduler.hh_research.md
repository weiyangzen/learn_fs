# sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.hh

## Purpose

`XrdScheduler.hh` declares `XrdScheduler`, the process-wide job scheduler interface used by XRootD server components for immediate work, delayed work, worker pool management, stats, and child-process reaping. The file was read completely.

## Important APIs, Types, and Functions

`XrdScheduler` inherits `XrdJob` so the scheduler can schedule its own idle-monitor job. Public APIs are `Active()`, `Cancel()`, `canStick()`, `DoIt()`, `Fork()`, `Reaper()`, `Run()`, immediate/list/timed `Schedule()`, `setParms()`, `Start()`, `Stats()`, `TimeSched()`, and `setNproc()`. Statistical counters exposed as public fields include `num_TCreate`, `num_TDestroy`, `num_Jobs`, `max_QLength`, and `num_Limited`. Constructors cover modern trace, ABI-compatible old trace, and standalone modes.

## Control Flow

The header exposes two scheduling planes: FIFO immediate work via `WorkFirst`/`WorkLast` and sorted delayed work via `TimerQueue`. `Start()` is the lifecycle entry point; workers run `Run()`, timed dispatch runs `TimeSched()`, and the scheduler's own `DoIt()` handles idle cleanup.

## State and Persistence Behavior

The class owns mutable in-memory counters and queues protected by dedicated mutexes. `WorkAvail` is the work semaphore; `TimerRings` wakes the timer thread when a new earliest timed job arrives; `firstPID` is the reaper list. No on-disk state is declared.

## Dependencies and Integration Points

The header depends on `XrdSysPthread.hh` synchronization wrappers and `XrdJob.hh`. It forward-declares tracing and logging types to keep the public scheduler interface light. `MAX_SCHED_PROCS` and `DFL_SCHED_PROCS` define scheduler resource-limit policy used by the implementation.

## Risks and Edge Cases

Several counters are public, so external code can observe and potentially depend on implementation details. `Active()` computes a non-locked snapshot and can be approximate. Job ownership is not explicit in the type signatures, so misuse can lead to jobs being queued while stack-allocated or deleted. `canStick()` also reads unsynchronized counters.

## Test Signals

Compile checks should cover all constructor overloads for ABI compatibility. Behavioral tests should validate public counters, queue state transitions, and that timed and immediate scheduling remain compatible with `XrdJob` subclasses.
