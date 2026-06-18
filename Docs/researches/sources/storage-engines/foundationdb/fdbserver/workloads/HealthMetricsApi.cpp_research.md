# sources/storage-engines/foundationdb/fdbserver/workloads/HealthMetricsApi.cpp

## Purpose
Attachable workload that polls `Database::getHealthMetrics` and validates that aggregate and optional detailed health metrics are populated and continue changing during a running simulation.

## Important APIs, types, and functions
`HealthMetricsApiWorkload` derives from `TestWorkload`. It tracks aggregate worst storage queue, durability lag, tlog queue, limiting values, and detailed per-storage/per-tlog queue, CPU, and disk usage. Key methods are `setup`, `start`, `check`, `getMetrics`, and `healthMetricsChecker`.

## Control flow
Setup optionally waits for detailed-health cache staleness and clears cached detailed stats when `sendDetailedHealthMetrics` is false. Start runs `healthMetricsChecker` until `testDuration`. The checker delays at `healthMetricsCheckInterval`, fetches health metrics, marks the workload failed if values repeat longer than `maxAllowedStaleness`, records maxima, emits trace events, and marks `gotMetrics` after both storage and tlog detailed maps appear.

## State and persistence behavior
The workload does not write database keys. It mutates client-side cached health metrics only in the non-detailed setup path. All lasting state is in workload counters/booleans used by `check`.

## Dependencies and integration points
Integrates with client health metrics aggregation, cached detailed metrics in `Database`, worker/storage/tlog metric producers, `CLIENT_KNOBS->DETAILED_HEALTH_METRICS_MAX_STALENESS`, and trace logging.

## Risks and test signals
The check tolerates receiving no full metric sample, but fails if received metrics stop changing or required values are zero/nonzero contrary to the detailed flag. It is timing-sensitive and can be noisy on idle clusters. Signals are trace events for metric values, `HealthMetricsStoppedUpdating`, `IncorrectHealthMetricsState`, and exported perf metrics for the maxima.
