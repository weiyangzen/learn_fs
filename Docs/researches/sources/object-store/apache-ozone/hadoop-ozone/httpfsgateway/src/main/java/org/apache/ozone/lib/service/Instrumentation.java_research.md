# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Instrumentation.java

## Purpose
`Instrumentation` defines the metrics and runtime snapshot API for the HttpFS service framework.

## Important APIs, types, and functions
`Cron` measures operations with `start()` and `stop()`. `Variable<T>` supplies dynamic values. The service API increments counters, records cron timings, adds variables, adds one-second samplers, and returns a grouped snapshot map.

## Control flow
Implementations create cron objects around measured work, register variables/samplers, and expose a live snapshot for JSON rendering or diagnostics.

## State and persistence behavior
The interface defines in-memory metrics only. No durable persistence is implied.

## Dependencies and integration points
`InstrumentationService`, `SchedulerService`, and `FileSystemAccessService` use this API. `JSONProvider` and `JSONMapProvider` can serialize metrics-like maps and JSON-aware values.

## Risks and edge cases
The snapshot is typed as nested wildcard maps, so consumers need runtime knowledge of value types.

## Test signals
`TestHttpFSMetrics` verifies higher-level HttpFS metrics updates for create/append byte counts.
