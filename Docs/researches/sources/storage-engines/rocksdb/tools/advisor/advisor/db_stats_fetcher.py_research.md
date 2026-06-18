# sources/storage-engines/rocksdb/tools/advisor/advisor/db_stats_fetcher.py

## Purpose

`db_stats_fetcher.py` adapts RocksDB LOG statistics, db_bench perf context, and external ODS/rapido time series into the common Advisor `TimeSeriesData` interface.

## Important APIs, Types, and Functions

Classes are `LogStatsParser`, `DatabasePerfContext`, and `OdsStatsFetcher`. Important methods include `LogStatsParser.parse_log_line_for_stats`, `add_to_timeseries`, `fetch_timeseries`; `DatabasePerfContext.unaccumulate_metrics`; and ODS helpers `_get_string_in_quotes`, `_get_time_value_pair`, `_get_ods_cli_stime`, `execute_script`, `parse_rapido_output`, `parse_ods_output`, `fetch_timeseries`, `get_keys_from_conditions`, and `fetch_rate_url`.

## Control Flow

Log stats parsing scans LOG files by prefix, skips old files, groups log records, identifies `STATISTICS:` records, parses metric lines into lowercased keys, and populates `keys_ts`. Perf context wraps a provided metric timestamp map and optionally converts cumulative samples to deltas. ODS fetchers build shell commands, execute client tools, then parse tabular output into entity/key/timestamp maps.

## State and Persistence Behavior

State is in-memory `keys_ts`, `stats_freq_sec`, and duration windows. ODS execution overwrites `temp/stats_out.tmp` and `temp/stats_err.tmp`.

## Dependencies and Integration Points

It depends on Advisor log/time-series parsers, `subprocess`, `glob`, `re`, and external ODS/rapido clients. It feeds time-series rule conditions.

## Risks and Test Signals

Risks include shell execution, fixed temp files, fragile output parsing, numeric conversions, old-log filtering, and division issues in rate calculations. Tests cover burst detection, aggregate and per-epoch expression triggers, mocked fetches, and cumulative perf-context conversion.
