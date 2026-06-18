# sources/storage-engines/rocksdb/tools/advisor/advisor/rules.ini

## Purpose

`rules.ini` is the default expert-rule specification for the RocksDB Advisor. It describes symptoms, conditions, and configuration suggestions for write stalls, L0/compaction pressure, Bloom filter usefulness, latency spikes, and decompression overhead.

## Important APIs, Types, and Functions

The file defines `[Rule]`, `[Condition]`, and `[Suggestion]` sections consumed by `RulesSpec`. Conditions use `source=LOG`, `source=OPTIONS`, or `source=TIME_SERIES`; suggestions use `option`, `action`, optional `suggested_values`, and sometimes freeform `description`.

## Control Flow

At runtime the parser loads each section into objects. Log rules match stall regexes, option rules evaluate Python expressions over `options`, and time-series rules evaluate bursty or expression behavior over `keys`. Triggered rules cause suggestions such as increasing background flushes/compactions, write buffer size, L0 triggers, pending compaction byte limits, Bloom bits, cache size, or changing compression type.

## State and Persistence Behavior

The file is static configuration. It drives in-memory rule objects and later option updates; it does not persist results.

## Dependencies and Integration Points

It depends on exact parser keywords and RocksDB option names. It integrates with `rule_parser_example.py`, `config_optimizer_example.py`, and `ConfigOptimizer`.

## Risks and Test Signals

Risks include a likely typo `[Rules "tuning-iostat-burst"]` that is not a recognized `Rule` header, use of Python `eval`, option names that may drift from RocksDB, and thresholds that are workload-specific. Tests use reduced fixture rule files, so the full default file needs separate smoke coverage with representative logs/options/time-series data.
