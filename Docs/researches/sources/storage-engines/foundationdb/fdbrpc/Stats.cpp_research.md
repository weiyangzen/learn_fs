# sources/storage-engines/foundationdb/fdbrpc/Stats.cpp

## Purpose
`Stats.cpp` implements counter collections, periodic trace emission, latency bands, and latency samples for fdbrpc/Flow metrics. It bridges internal counters to `TraceEvent`, optional OpenTelemetry metrics, and StatsD message generation.

## Important APIs, Types, and Functions
Core methods include `Counter::operator+=`, `getRate`, `getRoughness`, `resetInterval`, `clear`, `CounterCollection::logToTraceEvent`, `CounterCollection::traceCounters`, `LatencyBands::addThreshold`, `LatencyBands::addMeasurement`, `LatencyBands::clearBands`, `LatencySample::addMeasurement`, and `LatencySample::logSample`.

## Control Flow
Counters accumulate interval deltas and squared inter-event timings. `traceCounters` delays once for initialization, resets all counters, then loops forever creating a trace event, logging every counter, applying a decorator, optionally tracking latest, and waiting the configured interval. `LatencyBands` lazily creates a `CounterCollection` when the first threshold is added, installs an infinity band and filtered counter, then places each measurement into the first upper-bound band. `LatencySample` records measurements in a DDSketch and periodically emits count, elapsed, min/max, mean, and percentiles, then clears the sketch.

## State and Persistence Behavior
All state is process-local and interval-based: counters, last event times, sketch buckets, event-cache tracking keys, random metric IDs, and recurring actor futures. No durable state is written. Emission mutates global metric collections when configured.

## Dependencies and Integration Points
The file depends on `fdbrpc/Stats.h`, `flow/IRandom.h`, `Knobs`, `OTELMetrics`, `TDMetric`, `Trace`, and `network`. It integrates with `MetricCollection::getMetricCollection`, `createStatsdMessage`, `createOtelGauge`, `TraceEvent::trackLatest`, and `g_network->getLocalAddress`.

## Risks and Edge Cases
`Counter` assumes non-empty names for capitalization. `Counter::getRoughness` can report negative sentinel values when no elapsed time exists. StatsD attribute vectors are currently built but not passed into message creation, so endpoint labels may be absent for StatsD. `LatencySample` labels `p50` using `sketch.mean()` while also logging `Median` as that value, which is semantically surprising. Periodic actors capture `this`, so owners must clear futures before destruction.

## Test Signals
Benchmarks in `BenchSamples.cpp` exercise `LatencyBands`, DDSketch-backed latency samples indirectly, and histogram sampling. Runtime trace output, OTEL histogram/gauge entries, and StatsD messages are the main integration signals.
