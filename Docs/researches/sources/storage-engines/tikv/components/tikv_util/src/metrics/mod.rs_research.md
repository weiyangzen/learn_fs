# sources/storage-engines/tikv/components/tikv_util/src/metrics/mod.rs

## Purpose
Aggregates TiKV utility metrics exports, conditionally selects platform process/thread collectors, provides Prometheus text dumping, defines shared counters/gauges, and converts internal maps to PD protobuf record pairs.

## Important APIs, Types, and Functions
- Conditional exports: Linux uses `threads_linux` and `process_linux`; other platforms use dummy modules.
- `monitor_allocator_stats`, `monitor_threads`, `monitor_process`, and `HistogramReader` are public metric entry points.
- `dump(should_simplify)` and `dump_to` gather and encode Prometheus metrics.
- Static metrics include `CRITICAL_ERROR`, `NON_TXN_COMMAND_THROTTLE_TIME_COUNTER_VEC`, its static auto-flush wrapper, and `INSTANCE_BACKEND_CPU_QUOTA`.
- `convert_record_pairs(HashMap<String,u64>)` produces `Vec<pdpb::RecordPair>`.

## Control Flow
`dump_to` gathers all Prometheus metric families. In full mode it encodes all families. In simplified mode it filters zero-valued counters and empty histograms before encoding, leaving other metric types untouched. Static metric declarations are registered through `lazy_static` when first accessed.

## State and Persistence Behavior
Metric state lives in the process-wide Prometheus registry. Dump output is a transient text snapshot. Static metrics persist for process lifetime once initialized.

## Dependencies and Integration Points
Depends on `prometheus`, `prometheus_static_metric`, `kvproto::pdpb`, platform-specific collectors, and allocator metrics. It is the central import point for TiKV components that need utility-level metrics.

## Risks
Duplicate metric registration can panic or return errors in submodules. Simplified dumping intentionally drops zero counters and empty histograms, so it is unsuitable for consumers that require full metric schemas. The typo in the comment does not affect behavior.

## Test Signals
`test_dump_metrics` registers counter, counter vec, histogram vec, and gauge metrics, checks full and simplified output are non-empty and duplicate-free, and verifies simplification reduces output until metrics receive samples.
