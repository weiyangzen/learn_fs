# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Scheduler.java

## Purpose
`Scheduler` defines the background scheduling service API for HttpFS internal jobs.

## Important APIs, types, and functions
It exposes overloads for scheduling `Callable<?>` and `Runnable` tasks with delay, fixed delay interval, and `TimeUnit`.

## Control flow
Implementations run tasks periodically and decide how to handle failures and server status.

## State and persistence behavior
The interface owns no state. `SchedulerService` owns an executor.

## Dependencies and integration points
`InstrumentationService` uses the scheduler to sample metrics every second. `FileSystemAccessService` uses it to purge idle cached filesystem instances.

## Risks and edge cases
Scheduled tasks should tolerate repeated execution and exceptions because failures are logged and counted by the implementation.

## Test signals
No direct tests in this subset; service boot and filesystem cache purge wiring depend on this API.
