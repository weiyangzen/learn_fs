# sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_linux.rs

## Purpose
Collects Linux per-thread Prometheus metrics and provides sampled per-thread CPU/read/write rate aggregation by thread name.

## Important APIs, Types, and Functions
- `monitor_threads(namespace)` registers `ThreadsCollector` for the current process.
- `Metrics` owns gauge vectors for per-thread CPU totals, IO totals, thread states, and voluntary/nonvoluntary context switches.
- `ThreadsCollector` synchronously scrapes thread IDs, `/proc/<pid>/task/<tid>/stat`, IO, and status.
- `ThreadInfoStatistics` records interval CPU and IO rates by thread command/name.
- `TidRetriever` caches thread ID lists and backs off refresh interval from 15 seconds to 10 minutes when unchanged.
- Helpers include `sanitize_thread_name`, `state_to_str`, `collect_metrics_by_name`, and `update_metric`.

## Control Flow
Prometheus collection locks the metric set and TID retriever. If the TID list changes, all metric vectors are reset to avoid stale labels. For each thread, it reads full stat, resolves a sanitized name from `THREAD_NAME_HASHMAP` when available or `/proc` command otherwise, sets CPU total, increments state count, and optionally sets IO and context-switch metrics.
`ThreadInfoStatistics::record` computes elapsed wall time, clears rate maps, refreshes TIDs, reads totals, and converts positive deltas into per-second rates. CPU deltas are pre-multiplied by 100 so results are percentages.

## State and Persistence Behavior
Prometheus collector state persists per registered collector and is refreshed on scrape. `ThreadInfoStatistics` stores last instant, known TID names, previous totals, and current rates in memory. TID caching is adaptive and process-local.

## Dependencies and Integration Points
Depends on `procinfo`, `prometheus`, `crate::sys::thread` for IDs/stats/name map, and `crate::time::Instant`. It integrates with thread wrapper hooks that populate `THREAD_NAME_HASHMAP`.

## Risks
Frequent TID scanning can fragment memory, so caching is deliberate but can delay visibility of short-lived threads. Metrics label cardinality tracks thread names and IDs. `thread::thread_ids(pid).unwrap()` in `TidRetriever` can panic if `/proc` access fails. Rate computation ignores zero/negative deltas, so resets can leave stale previous totals.

## Test Signals
Tests cover thread IO visibility, IO rate accumulation, high-CPU percentage sampling, thread-name sanitization, and collector smoke registration/collection.
