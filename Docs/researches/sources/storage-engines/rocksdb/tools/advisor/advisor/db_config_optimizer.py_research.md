# sources/storage-engines/rocksdb/tools/advisor/advisor/db_config_optimizer.py

## Purpose

This module contains the Advisor optimization loop that applies rule suggestions to RocksDB OPTIONS, benchmarks each candidate configuration, and backtracks when throughput does not improve.

## Important APIs, Types, and Functions

`ConfigOptimizer` exposes static helpers `apply_action_on_value`, `improve_db_config`, `pick_rule_to_apply`, `apply_suggestions`, and `get_backtrack_config`, plus the instance method `run`. Constants `SCOPE` and `SUGG_VAL` name output concepts.

## Control Flow

`run` deep-copies the initial options, bootstraps a benchmark, loads and validates rules, triggers rules from returned data sources, applies one selected rule, updates options, reruns the benchmark, compares metrics through `bench_runner.is_metric_better`, and either backtracks or reloads/retriggers rules for the next iteration. Selection prefers a still-triggered previous rule after improvement, otherwise the first untried rule.

## State and Persistence Behavior

State is held in mutable `DatabaseOptions`, current/updated option dictionaries, triggered rules, and a `rules_tried` set. Persistent side effects are delegated to benchmark runs and generated OPTIONS files.

## Dependencies and Integration Points

It depends on `DatabaseOptions`, `NO_COL_FAMILY`, and `Suggestion.Action`. It integrates rule parser output with benchmark data sources and the db_bench runner.

## Risks and Test Signals

Risks include random choice among suggested values, `assert`-based validation, integer-only 30 percent option changes, recursion when diffs are empty, and narrow throughput-only optimization. Signals include unit tests around option diffs/actions plus end-to-end optimizer runs that show rule application, backtracking, and final option generation.
