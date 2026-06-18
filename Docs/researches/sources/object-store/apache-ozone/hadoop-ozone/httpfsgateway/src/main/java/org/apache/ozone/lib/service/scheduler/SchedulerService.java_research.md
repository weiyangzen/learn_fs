# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/SchedulerService.java

## Purpose
`SchedulerService` implements periodic background task execution for HttpFS services, with instrumentation and server-status gating.

## Important APIs, types, and functions
It reads `scheduler.threads` from service config, creates a `ScheduledThreadPoolExecutor`, and implements both `schedule(Callable, ...)` and `schedule(Runnable, ...)`. The callable scheduler wraps each run with counters for executions, skips, failures, and cron timing. `destroy()` shuts down the executor and waits up to 30 seconds.

## Control flow
If the server is `HALTED`, scheduled work is skipped and a `.skips` counter is incremented. Otherwise it increments `.execs`, starts a cron, invokes `call()`, records failures, and adds timing in a finally block. Scheduling uses fixed delay rather than fixed rate.

## State and persistence behavior
State is the scheduled executor and queued tasks. There is no durable persistence.

## Dependencies and integration points
It extends `BaseService`, depends on `Instrumentation`, wraps runnables with `RunnableCallable`, and is used by instrumentation sampling and filesystem cache purging.

## Risks and edge cases
Scheduling after shutdown throws `IllegalStateException`. A task that blocks can delay its own next run under fixed-delay semantics. Interrupted shutdown logs but does not restore the interrupt flag.

## Test signals
Indirect service boot and filesystem purge behavior depend on this service. Instrumentation counters provide runtime visibility into task execution/failure.
