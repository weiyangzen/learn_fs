# sources/storage-engines/rocksdb/tools/advisor/test/test_db_stats_fetcher.py

## Purpose

This module tests time-series condition evaluation for LOG-derived statistics and cumulative perf-context conversion.

## Important APIs, Types, and Functions

It imports `LogStatsParser`, `DatabasePerfContext`, `NO_ENTITY`, `Condition`, and `TimeSeriesCondition`. Tests cover bursty triggers, evaluate-expression triggers with `latest` aggregation, evaluate-expression triggers per epoch, and `DatabasePerfContext.unaccumulate_metrics`.

## Control Flow

Setup reads a fixture `log_stats_parser_keys_ts` into `LogStatsParser.keys_ts`, then mocks `fetch_timeseries` so condition evaluation uses deterministic data. Conditions are built dynamically by converting base `Condition` objects into `TimeSeriesCondition` and setting keys, behavior, thresholds, windows, expressions, and aggregation operations.

## State and Persistence Behavior

The tests are in-memory except for reading the fixture stats file. Condition triggers are mutable per test.

## Dependencies and Integration Points

They cover `TimeSeriesData` behavior used by `LogStatsParser`, `DatabasePerfContext`, and ODS-backed stats.

## Risks and Test Signals

Signals are exact trigger dictionaries and unaccumulated metric maps. Risks include timestamp alignment assumptions, floating-point exactness, and lack of direct ODS parser coverage.
