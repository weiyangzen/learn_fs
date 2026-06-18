# sources/storage-engines/wiredtiger/src/conf/conf_compile.c

## Purpose
This file compiles textual API configuration strings into compact `WT_CONF` structures that can be reused or copied into API call buffers. It is a performance-oriented alternative to repeatedly parsing strings in hot paths.

## Important APIs, Types, and Functions
`__wt_conf_compile` compiles a user-visible configuration string and returns an opaque pointer into `conn->conf_dummy`. `__wt_conf_compile_api_call` builds or reuses a compiled config for one API invocation. `__wt_conf_compile_init` precompiles default configurations for all compilable APIs at connection startup. `__wt_conf_compile_discard` frees compiled state. Internal helpers include `__conf_compile`, `__conf_compile_value`, `__conf_compile_config_strings`, `__conf_verbose`, and `__conf_compile_free`.

## Control Flow
Compilation parses key/value pairs with `__wt_config_next`, uses generated jump tables and `bsearch` to find `WT_CONFIG_CHECK` metadata, maps key ids to one-based entries in `WT_CONF.value_map`, and stores values as defaults, nondefaults, binding descriptors, or sub-configuration references. Category/list values may recurse into subconfig check arrays after stripping matching brackets. Initialization allocates `conf_dummy`, `conf_array`, and `conf_api_array`, then compiles base configs for each compilable API. API calls either return a precompiled config, copy the default compiled superstructure and overlay caller config, or return the default when no config is supplied.

## State and Persistence
Connection-level mutable state includes `conn->conf_dummy`, `conn->conf_array`, `conn->conf_size`, `conn->conf_max`, and `conn->conf_api_array`. `WT_CONF` itself is designed as a position-independent superstructure containing an array of `WT_CONF` nodes followed by `WT_CONF_VALUE` entries. Source strings for explicitly compiled configs are owned and freed with the compiled object. This is in-memory state only, but it controls how persistent object creation and runtime API options are interpreted.

## Dependencies and Integration Points
The file depends on generated config metadata in `config.h`, `conf.h`, `conf_keys.h`, validation helpers such as `__wt_conf_check_one`, and the generic parser in `config.c`. Public integration comes through `WT_CONNECTION::compile_configuration`, `WT_SESSION::bind_configuration`, and API wrapper macros in `api.h`. Verbose reconstruction uses `__wt_conf_gets_func` to cross-check compiled lookups against normal config parsing.

## Risks and Edge Cases
The layout arithmetic is dense: sub-config indexes, value-table offsets, default bitmaps, and one-byte value-map positions must stay consistent with generated sizing. Binding placeholders are allowed only in explicit compilation and must not appear twice for the same key. The returned compiled string is an address into `conf_dummy`; copying it as a normal string loses identity. `conf_size` uses atomic fetch-add, so overflow handling must avoid leaking compiled entries.

## Test Signals
`test/csuite/wt11126_compile_config` is the most direct signal, with additional coverage from `test/csuite/config` and API tests that use compiled configurations. Debug verbosity can reconstruct configs and assert boolean/string invariants. Fuzz-like config parser tests are useful for nested categories, duplicate keys, bindings, and invalid types.
