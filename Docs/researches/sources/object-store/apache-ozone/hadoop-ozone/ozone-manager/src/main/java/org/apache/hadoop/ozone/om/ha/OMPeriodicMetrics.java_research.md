# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMPeriodicMetrics.java

Purpose: `OMPeriodicMetrics` is a reusable framework for metrics that need periodic recomputation on a single daemon thread.

Important APIs and types: Subclasses implement `updateMetrics()` returning true on successful update. Public methods are `start`, `stop`, and `getLastUpdateTime`. Construction requires a non-empty task name and positive update interval.

Control flow: `start` is idempotent, creates a single-thread scheduled executor, and schedules `updateMetrics` with fixed delay starting immediately. Successful updates set `lastUpdateTime`; thrown exceptions are logged and do not stop scheduling. `stop` cancels without interrupting current work, shuts down the executor, waits up to 30 seconds, then forces shutdown and waits briefly if needed.

State and persistence behavior: Runtime state includes executor, future, last update timestamp, task name, interval, and a `started` flag. No durable state is written.

Dependencies and integration points: OM HA and background metric sources can subclass it to decouple metric calculations from request paths.

Risks and test signals: `started` is volatile but `start`/`stop` are not synchronized, so concurrent calls can race. A long-running `updateMetrics` delays shutdown. Tests should cover constructor validation, duplicate start, exception handling, timestamp update only on true, stop before start, forced shutdown, and concurrent start/stop behavior.
