# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutorMetrics.java

Purpose: `EventExecutorMetrics` is the Hadoop Metrics2 source used by event executors in `org.apache.hadoop.hdds.server.events`. It records executor lifecycle counters for queued, scheduled, successful, failed, dropped, long-running, and long-queue-wait events.

Important APIs/types/functions: the constructor accepts a metrics source `name` and `description`, creates a `MetricsRegistry`, and calls `init()`. `init()` registers this instance with `DefaultMetricsSystem`; `unregister()` removes the source. `getMetrics()` snapshots the registry into a `MetricsRecordBuilder`. Public increment methods mutate the `MutableCounterLong` fields, and getters expose counter values to executor implementations and tests.

Control flow: executors create one metrics object when they are constructed, increment counters around enqueue/schedule/handler execution, and unregister during close. Metrics fields are injected by the Metrics2 annotation machinery when the source is registered.

State and persistence: all state is in-process Metrics2 counter state; there is no durable persistence. Source names must remain unique in the default metrics system or registration/unregistration collisions can occur.

Dependencies/integration: used by `SingleThreadExecutor` and `FixedThreadPoolWithAffinityExecutor`; exposed through Hadoop Metrics2 and consumed by Prometheus export via the HTTP metrics sink path. It depends on `DefaultMetricsSystem`, `MetricsRegistry`, `MetricsSource`, and `MutableCounterLong`.

Risks: duplicate registrations with the same source name may overwrite or fail depending on Metrics2 behavior. `incrementDropped(int)` accepts any integer, so callers should pass non-negative drop counts. Metrics fields are package-initialized by Metrics2 registration, so using an unregistered object in isolation would leave counters unset.

Test signals: event queue tests assert executor counters indirectly through executor APIs; `FixedThreadPoolWithAffinityExecutor` tests cover dropped/queued/scheduled semantics. Metrics correctness is also visible through integration with the HTTP Prometheus metrics path.
