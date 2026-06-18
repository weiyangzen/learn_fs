# sources/storage-engines/wiredtiger/src/conf/conf_bind.c

## Purpose
This file binds runtime varargs values to placeholders in a previously compiled WiredTiger configuration string. It supports the public `WT_SESSION::bind_configuration` path.

## Important APIs, Types, and Functions
`__wt_conf_bind(WT_SESSION_IMPL *session, const char *compiled_str, va_list ap)` is the only function. It uses `WT_CONF`, `WT_CONF_BINDINGS`, `WT_CONF_BIND_DESC`, and `WT_CONFIG_ITEM`. Binding descriptors come from `conf_compile.c` when `%d` or `%s` placeholders are compiled.

## Control Flow
The function resolves `compiled_str` to a compiled `WT_CONF` with `__wt_conf_get_compiled`; failure returns `EINVAL`. It clears `session->conf_bindings`, iterates over `conf->binding_descriptions`, copies each descriptor into the session binding slot, reads the next vararg according to descriptor type, and fills the corresponding `WT_CONFIG_ITEM`. Numeric and boolean placeholders read `int64_t`. String and ID placeholders read `const char *`, set string length, coerce literal `true` and `false` to boolean constants, and otherwise validate choices with `__wt_conf_check_choice`.

## State and Persistence
The function mutates only `session->conf_bindings`, making bindings session-local and temporary. It does not alter the compiled configuration object. Bound values later satisfy `CONF_VALUE_BIND_DESC` lookups in `conf_get.c`; missing or stale bindings cause a runtime error.

## Dependencies and Integration Points
It depends on compiled configuration metadata from `conf_compile.c`, choice constants from generated config code, and `__wt_conf_get_compiled`. It is called from `session_api.c` in the implementation of `bind_configuration`.

## Risks and Edge Cases
Varargs type agreement is critical and cannot be checked by the compiler. `WT_CONF_BIND_VALUES_LEN` is small, so compiler-side binding counts must remain within session storage limits. Strings are not copied; callers must keep them valid for the use window. Boolean string coercion is required for compatibility with non-compiled config parsing and fast choice comparisons.

## Test Signals
`test/csuite/config` and `test/csuite/wt11126_compile_config` exercise compile/bind flows. Useful cases include `%d`, `%s`, boolean strings, invalid choices, unbound compiled configs, and repeated binds on the same session.
