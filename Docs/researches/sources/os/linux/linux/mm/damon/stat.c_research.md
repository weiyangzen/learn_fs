# File Research: sources/os/linux/linux/mm/damon/stat.c

DAMON module that exposes simple system memory access statistics.

Exported module parameters:
- `enabled`: starts/stops the stat context.
- `estimated_memory_bandwidth`: read-only estimated accessed bytes per second.
- `memory_idle_ms_percentiles[101]`: read-only idle-time percentiles.
- `aggr_interval_us`: read-only current aggregation interval.

Key behavior:
- Builds an exclusive physical-address DAMON context over the full System RAM span.
- Uses default 5 ms sampling, 100 ms aggregation, 60 s ops update, 10-1000 regions.
- Enables interval autotuning toward a 4% observed access ratio with sample interval bounded from 5 ms to 10 s.
- Repeated `damon_call()` refreshes stats at most every 5 seconds.
- Bandwidth estimate sums region size multiplied by access count, scaled by aggregation interval.
- Idle percentiles sort regions by signed idleness: accessed regions are represented as negative age and idle regions as positive age.
- `enabled_store()` defers startup if DAMON is not initialized yet, allowing command-line configuration before init.

Lifecycle:
- `damon_stat_start()` destroys stale stopped context, builds a new one, starts DAMON exclusively, and registers the repeated stat callback.
- `damon_stat_stop()` stops DAMON, destroys the context, and clears the global pointer.
