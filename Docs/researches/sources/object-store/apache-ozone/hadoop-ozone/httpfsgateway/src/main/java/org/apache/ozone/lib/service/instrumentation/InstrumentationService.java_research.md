# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/InstrumentationService.java

## Purpose
`InstrumentationService` is the in-memory metrics implementation for the HttpFS service framework. It tracks counters, timers, variables, sampled rates, JVM memory variables, environment, and system properties.

## Important APIs, types, and functions
`init()` creates concurrent maps and lock guards, initializes the snapshot map, and registers JVM memory variables. `createCron()`, `incr()`, `addCron()`, `addVariable()`, `addSampler()`, and `getSnapshot()` implement the interface. Nested `Cron` records own and total time, `Timer` keeps a ring buffer of recent cron values and JSON serialization, `VariableHolder` wraps live variables, `Sampler` maintains a rolling sum/rate, and `SamplersRunnable` samples every second.

## Control flow
Post-init obtains `Scheduler` and schedules sampler execution with zero delay and one-second interval when a scheduler is present. Metric containers are lazily created per group/name with `computeIfAbsent` under locks. Timers call `cron.end()` before storing values.

## State and persistence behavior
All state is in-memory and concurrent. Snapshot includes live `System.getenv()` and `System.getProperties()` maps plus dynamic metric structures. No metrics are written to disk.

## Dependencies and integration points
It extends `BaseService`, implements `Instrumentation`, uses the `Scheduler` service, Hadoop `Time`, JSON.simple, and Java concurrent primitives. `SchedulerService` and `FileSystemAccessService` record counters/timers through it.

## Risks and edge cases
`Timer#getValues()` assumes at least one cron has been added; reading a never-used timer could index `-1`. Re-adding a sampler with the same group/name reinitializes the sampler and appends it again to the sampling list. Snapshot exposes mutable live maps to consumers.

## Test signals
Indirect signals include scheduler instrumentation counters and `TestHttpFSMetrics` for higher-level byte and operation metrics.
