# sources/storage-engines/rocksdb/monitoring/statistics_test.cc

Purpose: Unit tests for statistics enum/name-map consistency and configurable statistics objects with empty names.

Important APIs/types/functions: `SanityTickers` asserts `TickersNameMap` length and enum order. `SanityHistograms` does the same for `HistogramsNameMap`. `NoNameStats` defines a minimal `DefaultNameStatistics` with `Name() == ""` and an `inner` customizable shared pointer option.

Control flow: Map sanity tests iterate enum values and compare the stored enum in each pair. The no-name test verifies `ToString(ConfigOptions)` for a nameless stats object omits options even before and after configuring `inner=`.

State/dependencies: Uses RocksDB test harness, options type info, convenience/customizable infrastructure, and stack trace setup in main.

Risks/test signals: The suite is a strong guard against enum/name-map drift but does not test hot-path per-core aggregation. The no-name test covers a configuration edge case for wrapped stats objects.
