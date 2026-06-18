# sources/storage-engines/rocksdb/monitoring/statistics.cc

Purpose: Implements RocksDB statistics names, construction/registration, option integration, and `StatisticsImpl` aggregation behavior.

Important APIs/types/functions: Defines `TickersNameMap` and `HistogramsNameMap` mapping public enum order to string names. `CreateDBStatistics` constructs `StatisticsImpl`. `Statistics::CreateFromString` registers and loads built-in or custom stats. `StatisticsImpl` implements ticker reads/sets/resets, histogram reads, tick/histogram recording, full reset, `ToString`, `getTickerMap`, and `HistEnabledForType`.

Control flow: Hot-path updates record into `per_core_stats_.Access()` with relaxed atomics and optional forwarding to wrapped `stats_`. Aggregate operations lock `aggregate_lock_`, iterate all core-local slots, and merge ticker/histogram values. `setTickerCount` assigns the requested count to core 0 and zeroes other cores. `Reset` clears all tickers and histograms.

State and dependencies: Maintains optional inner `Statistics`, an aggregate mutex, and cache-line-aligned `CoreLocalArray<StatisticsData>` containing ticker atomics and histogram arrays. It depends on custom object loading/options, convenience APIs, histogram implementation, and string utilities.

Risks/test signals: The name maps must stay in enum order; tests assert this. Aggregation can be expensive because it scans all core-local slots and merges histograms. Stats-level gates skip tickers or histograms based on configured `StatsLevel`. ToString uses fixed temp buffers and asserts on truncation.
