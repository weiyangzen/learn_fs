# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat.py

## Purpose
This module defines metric extractors and aggregators for the performance runner. It turns stat-file text or JSON records into values suitable for Evergreen/Atlas output.

## Important APIs, Types, and Functions
`PerfStat` performs regex matching, conversion, trimmed-average aggregation, and output formatting. Subclasses implement special behavior: `PerfStatMinMax`, `PerfStatCount`, `PerfStatLatency`, `PerfStatLatencyWorkgen`, and `PerfStatDBSize`.

## Control Flow
Each stat object searches one or more files for matching values, `add_values` converts and stores them, and `get_value_list` formats one or more report metrics. Latency classes parse `monitor.json` JSON lines or workgen stdout latencies. DB size sums files in the test home directory.

## State, Persistence, and Dependencies
State is the `values` list on each metric object. Dependencies include `glob`, `json`, `os`, `re`, stat-file naming conventions, and monitor JSON schemas.

## Integration Points, Risks, and Test Signals
It integrates with `PerfStatCollection.find_stats` and `perf_run.py` reports. Risks include empty `values` causing divide-by-zero, `PerfStatDBSize` passing a `DirEntry` to `os.path.getsize`, first-match-only glob behavior in count stats, and schema assumptions for wtperf/workgen JSON. Signals are extracted metric values and value lists.
