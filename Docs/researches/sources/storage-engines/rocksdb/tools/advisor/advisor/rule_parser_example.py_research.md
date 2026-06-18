# sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser_example.py

## Purpose

This command-line example runs the Advisor rule parser against existing RocksDB OPTIONS, LOG files, and optional ODS data to print triggered rules and their suggestions.

## Important APIs, Types, and Functions

`main(args)` creates `RulesSpec`, `DatabaseOptions`, `DatabaseLogs`, `LogStatsParser`, optional `OdsStatsFetcher`, and a `data_sources` map keyed by `DataSource.Type`. The argument parser requires rules spec, OPTIONS path, LOG prefix, and stats dump period, and accepts ODS client/entity/key-prefix/time bounds.

## Control Flow

Execution parses arguments, loads and validates rules, loads options, builds log and statistics data sources, appends ODS time-series source if requested, evaluates triggered rules, and prints details through `RulesSpec.print_rules`.

## State and Persistence Behavior

The script reads options/logs and may write ODS fetcher temp output files indirectly. Trigger state is held in memory on parsed rules and conditions.

## Dependencies and Integration Points

It integrates the parser modules as a standalone advisor diagnostic flow without running `db_bench` or optimizer iterations.

## Risks and Test Signals

Risks include missing files, ODS argument combinations that are not fully validated, parser side effects from external clients, and direct printing rather than structured output. Signals are successful CLI invocation on fixture options/logs and expected triggered rule names.
