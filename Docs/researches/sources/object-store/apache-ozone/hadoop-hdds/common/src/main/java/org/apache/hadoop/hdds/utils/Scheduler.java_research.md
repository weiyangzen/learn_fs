# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Scheduler.java

## Purpose
Small wrapper around `ScheduledExecutorService` for delayed and periodic Ozone utility work.

## Important APIs, Types, And Functions
Constructor creates a named daemon or non-daemon scheduled thread pool. Public methods are `schedule(Runnable, ...)`, `schedule(CheckedRunnable, ..., Logger, errMsg)`, `scheduleWithFixedDelay`, `isClosed`, and `close`.

## Control Flow
Tasks are submitted directly to the executor. The `CheckedRunnable` overload catches any `Throwable` and logs it instead of letting the scheduled executor suppress later work. `close()` marks `isClosed`, calls `shutdownNow()`, waits up to 60 seconds, preserves interrupt status, and nulls the executor reference.

## State And Persistence
State is the executor, volatile closed flag, and thread name. Scheduled tasks and futures are in-memory only.

## Dependencies And Integration Points
Depends on Java concurrent scheduling, Ratis `CheckedRunnable`, and SLF4J. It is a lifecycle helper for services needing background timers.

## Risks
`schedule()` does not reject based on `isClosed`; after `close()` it can hit `NullPointerException` or executor rejection. Threads all receive the same name, making multi-thread diagnostics less precise. `shutdownNow()` cancels pending work rather than draining gracefully.

## Test Signals
Useful tests cover delayed execution, fixed-delay execution, checked-runnable exception logging, close idempotency, interrupt preservation, and submissions after close.
