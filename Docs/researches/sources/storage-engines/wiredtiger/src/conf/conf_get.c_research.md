# sources/storage-engines/wiredtiger/src/conf/conf_get.c

## Purpose
This file retrieves values from compiled `WT_CONF` structures using generated packed key ids. It is the compiled-configuration equivalent of textual `__wt_config_gets` lookups.

## Important APIs, Types, and Functions
`__wt_conf_gets_func(WT_SESSION_IMPL *session, const WT_CONF *orig_conf, uint64_t orig_keys, int override_default, bool use_override_default, bool no_precompiled_def, WT_CONFIG_ITEM *value)` is the sole function. Callers usually reach it through macros such as `__wt_conf_gets`, `__wt_conf_getones`, and `__wt_conf_gets_def`.

## Control Flow
The function walks 16-bit key-id components packed into `orig_keys`. At each level, it reads the one-based `value_map` entry, fetches the corresponding `WT_CONF_VALUE`, shifts to the next key component, and switches on value type. Default items may be suppressed or overridden with a synthetic boolean. Nondefault items return directly when no nested keys remain. Binding descriptors fetch the session-bound value at the descriptor offset and verify the descriptor pointer matches. Subconfig entries move `conf` to the referenced nested `WT_CONF` and continue.

## State and Persistence
The function does not mutate compiled config state. It reads `session->conf_bindings` for bound placeholders and may fail if values have not been bound. Persistent behavior is indirect: all API decisions backed by compiled configs depend on this lookup returning the same value as the traditional parser.

## Dependencies and Integration Points
It depends on `WT_CONF`, `WT_CONF_VALUE`, `WT_CONF_BIND_DESC`, `WT_CONF_BIND_VALUES_LEN`, default bitmap macros, and generated key ids. It is called heavily through inline/macros in `conf.h` and `conf_inline.h`, including from verbose reconstruction in `conf_compile.c` and API paths that accept compiled configs.

## Risks and Edge Cases
Packed key ids must be nonzero and within `WT_CONF_ID_COUNT`; incorrect generated ids can lead to not-found results or assertions. Binding descriptor pointer comparison intentionally catches stale or missing `bind_configuration` calls. Default override and `no_precompiled_def` behavior must match legacy `__wt_config_getones` and default-handling semantics.

## Test Signals
Compile-config csuite tests should compare compiled lookups against textual lookups for top-level and nested keys, defaults, overrides, `getones` semantics, bound placeholders, and missing bindings. Runtime API tests using compiled configs provide integration coverage.
