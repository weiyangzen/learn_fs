## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Stats.h

Purpose: Declares fdbrpc performance counters, collections, latency bands, and latency samples that feed trace events and OTEL metric models.

Important APIs/types/functions: `ICounter` extends `IMetric` with name/value/rate/roughness/reset methods. `CounterCollection` owns groups of counters and can log them to trace events or periodically trace with decoration. `Counter` tracks integer value, interval delta, rate, and roughness; it emits an `Int64MetricHandle`. `SpecialCounter<F>` registers computed integer counters. `LatencyBands` builds threshold counters for latency ranges. `LatencySample` records latency measurements into `DDSketch` and emits tail latencies.

Control flow: Counters register with a collection, accumulate values through increments, and reset interval state after logging. `CounterCollection::traceCounters()` schedules repeated trace logging. `LatencyBands` inserts thresholds and increments matching bands for each measurement. `LatencySample` maintains a sketch and logs periodically.

State and persistence behavior: Runtime metric state is in-memory. Metric data is exported through trace events and OTEL handles rather than durable storage. `CounterCollection` destructor calls `remove()` on counters marked for removal, which is how heap-allocated `SpecialCounter` instances clean up.

Dependencies and integration points: Depends on Flow errors, random, knobs, OTEL metrics, serializer, TDMetric, Swift support, and `DDSketch`. `TSSMetrics` builds on `CounterCollection` and `Counter`.

Risks: Counter lifetime must match collection lifetime; `SpecialCounter` deletes itself via `remove()`. Roughness calculation treats large deltas as repeated events and can be sensitive to interval reset timing. `SpecialCounter` rejects floating return types by static assertion, which can surprise callers. Logging futures must be cancelled/destructed correctly by owners.

Test signals: Counter increment/rate/roughness math, interval reset, trace formatting, skip-trace-on-silent behavior, special counter cleanup, latency band thresholds, DDSketch tail emission, and OTEL metric model compatibility.
