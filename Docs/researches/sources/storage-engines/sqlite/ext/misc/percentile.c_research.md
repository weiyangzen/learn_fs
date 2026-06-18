# sources/storage-engines/sqlite/ext/misc/percentile.c

Purpose: implements `median()`, `percentile()`, `percentile_cont()`, and `percentile_disc()` as aggregate/window functions over numeric input.

Important APIs/types/functions: `Percentile` stores all Y values, sort flags, and fraction state; `PercentileFunc` describes each registered variant. Main callbacks are `percentStep()`, `percentInverse()`, `percentValue()`, `percentFinal()`, `percentCompute()`, `percentSort()`, and `percentBinarySearch()`.

Control flow: step validates the fraction, enforces per-group fraction stability, ignores null Y, rejects nonnumeric/infinite Y, and appends or sorted-inserts values. Final/value sorts if needed and interpolates or selects the discrete value. Inverse removes values for sliding windows.

State and persistence: O(N) aggregate/window memory; no persistent writes.

Dependencies/integration: SQLite window function API and `SQLITE_SELFORDER1`.

Risks/test signals: memory growth, aggregate O(N log N) sort, window O(N*K) maintenance, duplicate inverse removal, fraction tolerance, and endpoint semantics. Test all variants, invalid inputs, nulls, large groups, windows, duplicates, discrete vs continuous output, and 0/100 or 0/1 endpoints.
