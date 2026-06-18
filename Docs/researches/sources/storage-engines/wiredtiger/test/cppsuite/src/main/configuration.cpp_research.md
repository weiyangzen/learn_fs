# sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.cpp

Purpose: Wraps WiredTiger config parsing and merges test-specific user configuration with generated default configuration.

Important APIs/types/functions: constructors load defaults via `__wt_test_config_match` or wrap a nested `WT_CONFIG_ITEM`. `get_*` and optional variants retrieve typed values through templated `get`. `get_throttle_ms` parses rates ending in `ms`, `s`, or `m`. `merge_default_config` recursively overlays user values onto default values. `split_config` tokenizes key/value pairs while respecting nested `()` and `[]`, sorts by key, and validates empty/malformed entries.

Control flow: top-level construction merges config then opens a WT config parser. Typed getters validate WT item types before conversion. Nested subconfigs allocate new `configuration` objects for component ownership.

State and persistence: owns config string and `WT_CONFIG_PARSER`; no direct persistence, but parsed values drive database/table/component behavior.

Dependencies/integration: depends on WT config parser, generated test config metadata, constants, logger, and `test_util`. Used throughout cppsuite components.

Risks and test signals: recursive merge assumes sorted key order and that user subconfigs start with `(`. `get_throttle_ms` uses substring matching, so malformed strings can throw or be misread. Parser/type errors fail fast through `testutil_die`.
