# sources/storage-engines/wiredtiger/src/config/config_check.c

## Purpose

`config_check.c` validates application-supplied WiredTiger configuration strings against a `WT_CONFIG_ENTRY` check table. It enforces allowed key names, expected value types, nested category schemas, custom checker callbacks, numeric min/max limits, and enumerated choices. This is the central runtime validation path used by public validation helpers and many API entry points unless a compiled configuration string can be trusted directly.

The file is performance-sensitive. Generated configuration tables can include sorted check arrays and ASCII jump tables, so validation can avoid scanning an entire method’s check table for every key.

## Important APIs, Types, and Functions

`__wt_config_check(WT_SESSION_IMPL *, const WT_CONFIG_ENTRY *, const char *, size_t)` is the exported validator. It returns success immediately for a NULL config, an entry with no check table, or a compilable config string that is already recognized as compiled for this connection. Otherwise it delegates to `__config_check`.

`__config_check` parses the supplied string with `__wt_config_init` or `__wt_config_initn`, iterates key/value pairs with `__wt_config_next`, validates each key and value against the matching `WT_CONFIG_CHECK`, recurses for category/subconfiguration values, runs optional checker callbacks, and enforces min/max and choices.

`__config_check_search` locates a `WT_CONFIG_CHECK` for a parsed key. For dynamic or unsized tables (`entries == 0`) it linearly scans until a NULL name. For generated tables it uses the first character and `checks_jump` to narrow the range, then calls `bsearch` with `__config_check_compare`.

`__config_check_compare` compares a parsed `WT_CONFIG_ITEM` key to a check name while respecting the parsed key length, preventing prefix matches from being accepted as full key matches.

`__wt_config_get_choice` checks whether a parsed item matches any string in a NULL-terminated `choices` list.

The important data contract is `WT_CONFIG_CHECK`: `name`, human-readable `type`, optional `checkf`, raw `checks`, optional `subconfigs`, generated `subconfigs_entries` and jump table, `compiled_type`, numeric bounds, and `choices`. `WT_CONFIG_ENTRY` supplies the check array, check count, jump table, and `compilable` flag.

## Control Flow

`__wt_config_check` is a gate. It deliberately treats missing inputs as successful because many callers make fast validation calls without first checking whether there is any config or check array. If a config has already been precompiled and the entry permits compiled configs, validation is skipped.

`__config_check` initializes a parser over either a NUL-terminated string or a bounded byte range. For each item, it first requires the key token type to be string or identifier. It searches for a matching check entry and fails with `EINVAL` on unknown keys.

Type enforcement is driven by `check->compiled_type`. Booleans accept native boolean tokens plus numeric 0 or 1; categories recurse into `check->subconfigs` over the value’s byte range; formats and strings do not add parser-level type restrictions; integers require `WT_CONFIG_ITEM_NUM`; lists require either an empty value or a struct. Unknown compiled types are treated as internal schema errors and return `EINVAL`.

After type checking, `checkf` is invoked if present. If `check->checks` is NULL, no min/max/choice validation is performed. Otherwise the value’s numeric `val` is compared with `min_value` and `max_value`, and configured `choices` are enforced. Structured choice values are iterated and every element must be found in the allowed choice list; scalar choices check the value directly.

Parser termination converts `WT_NOTFOUND` into success, preserving other parser errors.

## State and Persistence Behavior

This file does not own persistent state or mutate connection configuration. It reads immutable or connection-lifetime `WT_CONFIG_ENTRY` and `WT_CONFIG_CHECK` data and uses stack parser state. Recursive category validation re-enters the same logic with subconfig tables and a bounded view of the nested value.

The only durable effect is indirect: accepting or rejecting configuration controls whether callers proceed with API operations, connection open, schema changes, metadata updates, or dynamic method configuration. Error messages are delivered through the session’s error/event handling path.

Compiled configuration is an important state interaction. If `entry->compilable` is true and `__wt_conf_is_compiled(S2C(session), config)` returns true, this validator trusts that the string has already passed compilation-time checks and skips parsing.

## Dependencies and Integration Points

`config_check.c` depends on the core parser (`__wt_config_init`, `__wt_config_initn`, `__wt_config_next`, `__wt_config_subinit`), error macros, generated config metadata, `bsearch`, and compiled config detection from the `conf` subsystem.

It is called by `wiredtiger_config_validate` and `__wt_configure_method` in `config_api.c`, by connection open and reconfigure paths in `conn_api.c`, and by API macros in `src/include/api.h` via compiled-config setup. Generated entries and jump tables are produced in `config_def.c` and declared through `config.h`.

It aligns with `src/include/conf_inline.h`, where compiled config values use similar min/max and choice validation in `__wt_conf_check_one`; changes to validation semantics should be kept consistent across parsed and compiled paths.

## Risks and Edge Cases

Boolean validation intentionally accepts numeric 0 and 1. This matches existing parser behavior and compiled config tests, but it can surprise callers expecting only textual booleans.

Category validation maps any recursive `EINVAL` to `badtype`, then produces a generic expected-type message. Other errors propagate. This can reduce diagnostic specificity for nested unknown keys or invalid nested values.

For `WT_CONFIG_COMPILED_TYPE_STRING` and `WT_CONFIG_COMPILED_TYPE_FORMAT`, parser-level type restrictions are minimal. Any required semantic checks must live in `checkf` or choice metadata.

Min/max comparisons use `v.val` whenever `check->checks` is non-NULL. Check metadata must only install numeric bounds where the parsed value’s `val` is meaningful, or else non-numeric values could be compared against default numeric fields.

Structured choices reuse the local variable `v` for nested elements, so error messages for an invalid structured choice report the nested choice token as the value and the outer key as the key. This is intentional but worth preserving when refactoring.

The jump-table path assumes generated check arrays are sorted by key and that `checks_jump` bounds are valid for the table. Bad generator output can produce false unknown-key failures or out-of-range searches.

Keys beginning with non-ASCII or `0x7f` and above bypass the jump table range and fail as unknown. This matches the `WT_CONFIG_JUMP_TABLE_SIZE` 7-bit ASCII contract.

The fast path for compiled configs requires a non-NULL session. A NULL session cannot use `S2C(session)`, so standalone validation parses normally.

## Test Signals

Existing signals include public validation call sites, connection open/reconfigure validation, and config parser/compiled-config tests in `test/csuite/config/main.c`. Those tests explicitly account for numeric boolean input being converted to canonical booleans in compiled output.

Useful direct tests include unknown key rejection in both generated and dynamic `entries == 0` tables, prefix-key rejection, bounded non-NUL-terminated config validation, boolean numeric acceptance and invalid numeric rejection, integer/list/category type mismatches, nested category unknown key failures, min/max bounds, scalar and structured choices, custom `checkf` failures, and compiled-config skip behavior.
