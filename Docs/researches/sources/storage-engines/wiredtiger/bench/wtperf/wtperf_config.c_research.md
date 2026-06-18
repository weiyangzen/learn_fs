# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_config.c

## Purpose
`wtperf_config.c` implements wtperf option management. It expands the option list generated from `wtperf_opt_inline.h`, initializes defaults, parses config files and command-line option strings, parses workload thread groups, validates combinations, logs the effective config, and prints usage.

## Important APIs, Types, And Functions
Public functions are `config_opt_init`, `config_opt_cleanup`, `config_opt_file`, `config_opt_str`, `config_opt_name_value`, `config_sanity`, `config_opt_log`, `config_opt_print`, `config_opt_usage`, and `config_reopen`. Internal functions include `config_unescape`, `config_threads`, `config_opt`, `config_consolidate`, and `pretty_print`. The file uses WiredTiger's `WT_CONFIG_PARSER` to parse both top-level option strings and nested `threads=((...))` groups.

## Control Flow
Initialization copies the generated default struct and duplicates default strings so cleanup can free all string fields uniformly. `config_opt_file` reads lines, handles whitespace, comments, continuations, and overflow checks, then passes joined options to `config_opt_str`. `config_opt_str` scans `key=value` pairs, applies `config_opt`, and records each processed pair in `config_head`. `threads` values are delegated to `config_threads`, which builds `WORKLOAD` entries and sets global grow/shrink/truncate flags. `config_sanity` enforces cross-option rules before the benchmark runs.

## State And Persistence Behavior
The file mutates `CONFIG_OPTS`, `WTPERF.workload`, `workload_cnt`, `workers_cnt`, and wtperf flags. It persists the final processed configuration via `config_opt_log`, consolidating duplicate keys and concatenating repeated `conn_config` or `table_config` entries.

## Dependencies And Integration Points
It depends on `config_opt.h`, `wtperf_opt_inline.h`, WiredTiger config parsing, test utility allocation helpers, and `lprintf`. Its output feeds `wtperf.c` connection/table creation, workload scheduling, random selection, transactions, truncate, backup, scan, tiered, and monitoring behavior.

## Risks
Thread configuration is dense and rejects malformed values through a shared `goto err` path, so diagnostics can be coarse. Config queue recording happens after parsing each pair and can preserve implicit command order in ways tests may depend on. `CONFIG_STRING_TYPE` appends values while `STRING_TYPE` replaces, so changing an option's type changes user-visible semantics.

## Test Signals
Test config files with comments, continuations, escaped characters, repeated config keys, nested thread groups, invalid unknown options, invalid truncate mixes, readonly write workloads, scan table coupling, and grow/shrink value bounds. Verify `CONFIG.wtperf` consolidation and usage output after option list changes.
