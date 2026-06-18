# sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.cc

## Purpose

`XrdScheduler.cc` implements the core XRootD in-process scheduler: a pthread-backed work queue for `XrdJob` objects, a time scheduler for delayed jobs, adaptive worker creation and idle thread retirement, XML scheduler stats, and a SIGCHLD-based child reaper used after scheduler-mediated `fork()`. The file was read completely.

## Important APIs, Types, and Functions

External pthread entry points `XrdStartReaper`, `XrdStartTSched`, and `XrdStartWorking` bridge C pthread startup to `XrdScheduler::Reaper()`, `TimeSched()`, and `Run()`. Constructors initialize the scheduler from explicit `XrdSysError`/`XrdSysTrace`, deprecated `XrdOucTrace`, or a standalone stderr logger. `Boot()`, `Init()`, and `setNproc()` establish counters and resource limits. `Schedule()` has immediate, list, and timed overloads. `Cancel()` removes timed jobs. `Start()` launches the timer thread and initial workers. `Stats()` emits `<stats id="sched">`. `hireWorker()` starts worker threads and clamps limits after thread creation failure. `Fork()` and `Reaper()` track and reap child PIDs through local `XrdSchedulerPID` nodes.

## Control Flow

Immediate jobs are appended under `SchedMutex`, `WorkAvail.Post()` wakes workers, and `Run()` repeatedly marks a worker idle, waits on the semaphore, dequeues one job, optionally hires another worker if no idle worker remains, and calls `jp->DoIt()`. Timed jobs are sorted by `SchedTime` under `TimerMutex`; `TimeSched()` waits until the head expires, dequeues it, and reschedules it as immediate work. The scheduler itself is an `XrdJob`; `DoIt()` performs idle-worker layoffs and reschedules itself when `max_Workidl` is positive. `Fork()` adds child PIDs to a reaper list and lazily starts the reaper thread.

## State and Persistence Behavior

State is entirely in memory: worker counters, job queues, timer queue, child PID list, and statistics counters. Synchronization is split across `SchedMutex`, `DispatchMutex`, `TimerMutex`, and `ReaperMutex`. There is no durable persistence. The destructor is intentionally empty because the scheduler is treated as process-lifetime infrastructure.

## Dependencies and Integration Points

The scheduler depends on `XrdJob`, `XrdSysThread`, `XrdSysMutex`, `XrdSysSemaphore`, `XrdSysCondVar`, `XrdSysError`, `XrdSysTrace`, and platform process APIs. It is used by global server code, the send queue, stats reporter, config refresh jobs, and any module that schedules `XrdJob` work.

## Risks and Edge Cases

Timed `Cancel()` only unlinks a job and does not clear `NextJob`, so callers must not assume detached state. `Run()` self-deletes neither jobs nor worker objects; job lifetime is caller-owned unless the job's `DoIt()` deletes itself. `setNproc()` mutates process resource limits and must be validated on Linux-like systems with unusual `pid_max` or `RLIMIT_NPROC`. The reaper assumes `SIGCHLD` is blocked in `main()` for `sigwait()` semantics. Worker count correction after thread creation failure lowers `max_Workers` to the current count, which can permanently constrain the scheduler until reconfigured.

## Test Signals

Useful tests include queue ordering, timed scheduling order and cancellation, worker growth when backlog exceeds idle capacity, idle layoff after `max_Workidl`, stats XML sanity, failure injection for thread creation, and fork/reaper tests with normal exit and signal termination. Concurrency tests should stress simultaneous `Schedule()`, timed `Schedule()`, and `Cancel()`.
