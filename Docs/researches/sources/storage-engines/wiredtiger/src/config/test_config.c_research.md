# sources/storage-engines/wiredtiger/src/config/test_config.c

## Purpose

`test_config.c` is a generated configuration schema table for WiredTiger test workloads. It maps named test programs and scenarios to default configuration strings, compile-time validation descriptors, jump tables, sizing metadata, and the exported lookup function `__wt_test_config_match`.

## Important APIs, Types, and Functions

- `WT_CONFIG_CHECK`: describes allowed keys, value types, nested categories, constraints, compiled IDs, and numeric min/max bounds.
- `WT_CONFIG_ENTRY`: binds a method or test name to its default configuration string and validation table.
- `confchk_*_subconfigs`: nested schemas for metrics monitor, operation tracker, statistics, timestamp manager, workload manager, background compact, checkpoint, CRUD workload, and operation sizing fields.
- `confchk_*_jump`: generated jump tables sized by `WT_CONFIG_JUMP_TABLE_SIZE` to accelerate config key dispatch.
- `config_entries[]`: top-level mapping from test names such as `api_instruction_count_benchmarks`, `background_compact`, `bounded_cursor_perf`, `burst_inserts`, `cache_resize`, `hs_cleanup`, `operations_test`, `reverse_split`, and `search_near_*` to defaults and schemas.
- `__wt_test_config_match`: linear search by test name returning a `const WT_CONFIG_ENTRY *` or NULL.

## Control Flow

There is no runtime mutation beyond lookup. Configuration validation begins in consumers by calling `__wt_test_config_match(test_name)`. The function walks `config_entries` until `ep->method` is NULL, compares `test_name` with `strcmp`, and returns the matching static entry. The returned entry points to a default config string and a nested tree of `WT_CONFIG_CHECK` arrays. The core config validation code then uses the table and jump array to validate keys, types, categories, and bounds.

The generated schema is deeply shared. For example, common subconfigs such as `metrics_monitor`, `timestamp_manager`, and `workload_manager` are referenced by many test entries. Specialized entries add fields like `burst_duration` or `search_near_threads`, while most entries share the same broad operational template.

## State and Persistence Behavior

All state in this file is static const process memory. It does not read or write files, allocate memory, or persist anything. Its default configuration strings influence test database behavior when the corresponding test harness uses them, but this file itself is a schema and default catalog only.

## Dependencies and Integration Points

The file includes `wt_internal.h` and depends on generated config infrastructure from `dist/api_config.py`. It integrates with WiredTiger test and config machinery through `WT_CONFIG_ENTRY`, `WT_CONFIG_CHECK`, compiled config type enums, and the public internal lookup symbol `__wt_test_config_match`. It is not ordinary hand-written business logic; changes should normally be made in the generator inputs rather than in this generated C file.

## Risks and Edge Cases

- Because it is generated, manual edits are likely to be overwritten and can desynchronize schema metadata from generator sources.
- The linear lookup is simple and acceptable for a small static catalog, but duplicate names would silently select the first entry.
- Generated min/max bounds are enforcement points; incorrect bounds can make test workloads reject valid configs or accept unsafe values.
- Shared subconfig tables mean a change to one nested schema can affect many test entries.
- Default strings include nested categories and escaped line-split C strings; generator bugs here can produce valid C that is semantically invalid config.

## Test Signals

The file is itself test configuration data. Strong signals include successful config validation for every entry in `config_entries`, negative validation for out-of-range values such as invalid thread counts or key sizes, and harness tests that confirm `__wt_test_config_match` returns NULL for unknown tests. Build or generator tests should verify that `dist/api_config.py` can reproduce this file and that jump tables match their corresponding sorted key arrays.
