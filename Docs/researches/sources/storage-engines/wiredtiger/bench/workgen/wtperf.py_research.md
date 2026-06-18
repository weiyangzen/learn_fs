# sources/storage-engines/wiredtiger/bench/workgen/wtperf.py

## Purpose
`wtperf.py` is a partial translator and runner for `.wtperf` configuration files. It emits Python source using the workgen API, optionally prints that source, or executes it to emulate selected wtperf workloads through workgen.

## Important APIs, Types, and Functions
`Translator` owns parsing and translation. Important methods include `set_opt`, typed getters, `split_assign`, `split_config_parens`, `translate_table_create`, `translate_populate`, `parse_threads`, `calc_throttle`, and `translate_inner`. `OptionValue` tracks filename/line for diagnostics, `TranslateException` controls fatal parse exits, and the script-level loop handles `--python`, `--verbose`, `--pydebug`, and `.wtperf` arguments.

## Control Flow
The translator reads a config file, strips comments, parses `key=value`, forwards directly supported workload options, stores other supported options, validates combinations, and builds a Python program string. Generated code opens WiredTiger via workgen context helpers, creates tables, optionally populates data, builds thread operations, runs workload, writes latency output, closes the connection, and copies the original config plus generated `RUN.py` into `WT_TEST` after execution.

## State and Persistence Behavior
The script persists generated runtime artifacts under `WT_TEST`: `CONFIG.wtperf` and `RUN.py`. During normal execution it creates a temporary Python file, runs it, then removes it. It mutates translator state (`opts_map`, `opts_used`, `options`) while parsing.

## Dependencies and Integration Points
It depends on Python standard libraries plus built workgen, wiredtiger Python bindings, and the `bench/workgen/runner` package. It consumes `.wtperf` files used by benchmark suites and is an integration bridge between wtperf-style configs and workgen execution.

## Risks and Edge Cases
It supports only a known subset of wtperf options and intentionally errors on unknown options. Some generated strings are built by concatenation, so unusual quoting in config values can break generated Python. `split_assign` references `line` in an error path where it is not in scope. The `readonly` branch under `reopen_connection` contains a bare string expression instead of appending to `conn_config`, so readonly reopen appears ineffective. Divisibility requirements for multi-table population are strict and fatal.

## Test Signals
Useful tests include `--python` golden output for representative configs, execution of small `.wtperf` files, unsupported-option diagnostics with file/line numbers, multi-table/range partition validation, populate transaction behavior, checkpoint thread generation, and translated latency file production.
