# sources/storage-engines/wiredtiger/src/include/conf.h

## Purpose
`conf.h` defines WiredTiger's compiled-configuration representation. It turns generated configuration metadata into fixed-size, position-independent structures so API default/user configuration can be precompiled once and queried by numeric key IDs instead of reparsing strings on every call.

## Important APIs, Types, and Functions
The public-facing helpers are macros: `__wt_conf_gets`, `__wt_conf_getones`, and `__wt_conf_gets_def`, which wrap `__wt_conf_gets_func`/`__wt_conf_gets_def_func` with IDs from `WT_CONF_ID_STRUCTURE`. `WT_CONF_BINDINGS` and `WT_CONF_BIND_DESC` describe fast-path bound configuration values, including type, legal choices, and a session binding-table offset.

`WT_CONF` is the central compiled config object. It stores a default bitmap, diagnostic source/default/API strings, a `value_map` from key ID to `WT_CONF_VALUE`, counts and capacity for nested sub-configs and values, and binding descriptors. `WT_CONF_VALUE_TABLE_ENTRY` computes the inline value table address from `conf_value_table_offset`, keeping the structure copyable without pointer fixups.

The generated `WT_CONF_API_DECLARE` declarations define per-API superstructures such as `WT_CONF_API_TYPE(WT_SESSION, create)`, and sizing macros expose their total size/counts for compilation.

## Control Flow
API code compiles one or more config strings against a `WT_CONFIG_ENTRY`, producing a superstructure containing `WT_CONF[]` and `WT_CONF_VALUE[]`. Later callers use numeric IDs built from `conf_keys.h` through `WT_CONF_ID_STRUCTURE`. The lookup path first checks `bitmap_default` for cheap default detection, then consults `value_map` and the value table when an explicit value, binding descriptor, or sub-config entry is present.

## State and Persistence Behavior
The state is in-memory only. A `WT_CONF` owns only `source_config`; `api_config` and `default_config` are borrowed but guaranteed to outlive the compiled object. Position independence is a key persistence-like invariant inside memory: callers can copy the entire superstructure as bytes and still recover value-table entries via offsets.

## Dependencies and Integration Points
This header depends on generated IDs from `conf_keys.h`, parser/checking structures from `config.h`, bit-string helpers, `WT_CONFIG_ITEM`, and `WT_CONFIG_ENTRY`. It integrates with connection-level compiled config arrays in `WT_CONNECTION_IMPL` and session binding state.

## Risks and Edge Cases
The main risk is generator drift: the declared per-API counts must match generated checks/defaults, or compiled config writes can overrun or lookups can miss values. The 1-based `value_map` and offset-derived value table make off-by-one bugs costly. Bound values are optimized around a small fixed table (`WT_CONF_BIND_VALUES_LEN`), so adding many bound values requires coordinated sizing changes.

## Test Signals
Useful test signals are configuration parsing/validation suites, API open/create/reconfigure tests that exercise compiled and string configs equivalently, tests for default shortcuts, nested sub-config lookup, choice matching, and sanitizer coverage around generated count mismatches.
