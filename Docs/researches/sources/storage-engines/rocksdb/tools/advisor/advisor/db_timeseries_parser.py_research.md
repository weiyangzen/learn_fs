# sources/storage-engines/rocksdb/tools/advisor/advisor/db_timeseries_parser.py

## Purpose

This module defines the common time-series data-source abstraction used by Advisor rules. It evaluates bursty behavior and boolean expressions over fetched metrics.

## Important APIs, Types, and Functions

It defines `NO_ENTITY`, `TimeSeriesData`, enum `Behavior` (`bursty`, `evaluate_expression`), enum `AggregationOperator` (`avg`, `max`, `min`, `latest`, `oldest`), abstract `get_keys_from_conditions` and `fetch_timeseries`, plus concrete `fetch_burst_epochs`, `fetch_aggregated_values`, `check_and_trigger_conditions`, and `handle_evaluate_expression`.

## Control Flow

`check_and_trigger_conditions` asks the subclass for required keys, fetches them, filters entities that have all keys for each condition, and dispatches by behavior. Bursty conditions compute windowed rate changes. Expression conditions either aggregate each key once per entity or evaluate at each timestamp, then set trigger maps when the expression is true.

## State and Persistence Behavior

`keys_ts` stores entity -> key -> timestamp -> value. Condition triggers persist on condition objects until reset/reparsed.

## Dependencies and Integration Points

It depends on `math`, `DataSource`, and rule parser condition fields. Subclasses include `LogStatsParser`, `DatabasePerfContext`, and `OdsStatsFetcher`.

## Risks and Test Signals

Risks include `eval`, division by zero for percent rates, assuming aligned timestamps for multi-key expressions, and missing-key handling. Tests exercise burst windows, latest aggregation, non-aggregate expression evaluation, and cumulative perf metrics.
