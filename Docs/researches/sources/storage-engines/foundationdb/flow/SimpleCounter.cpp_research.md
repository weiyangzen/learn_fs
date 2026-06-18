<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SimpleCounter.cpp -->
# sources/storage-engines/foundationdb/flow/SimpleCounter.cpp
- Purpose: Reports process-local `SimpleCounter` metrics as trace events with Prometheus-compatible field names and includes concurrency unit tests.
- Important APIs/types/functions: `simpleCounterReport`, `hierarchicalToPrometheus`, `isValidPrometheusMetricName`, and tests `/flow/simplecounter/int64` and `/flow/simplecounter/double`.
- Control flow: `simpleCounterReport()` increments a report counter, retrieves integer and double counter registries, chunks counters by trace-event length budget, normalizes names, asserts Prometheus validity, and emits `SimpleCounters` trace events.
- State and persistence behavior: Counter storage is owned by `SimpleCounter<T>` registries outside this file. Reporting does not reset counters. Trace output is the observable persistence path.
- Dependencies and integration points: Depends on `flow/SimpleCounter.h`, Flow knobs for event length, `TraceEvent`, and unit-test registration. Name normalization maps hierarchical names like `/flow/counters/foo` to `flow_counters_foo`.
- Risks: Prometheus validation is assertion-only, so invalid names can abort debug/simulation builds. Chunk sizing assumes average field size and may still hit trace limits for unusual names. Tests intentionally run threaded increments that can be expensive.
- Test signals: Embedded tests validate integer and floating atomicity under 10 threads, registry growth, exact floating sums using representable increments, and `simpleCounterReport()` assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SimpleCounter.cpp -->
