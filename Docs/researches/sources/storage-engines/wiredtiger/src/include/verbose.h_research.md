<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verbose.h -->
# Research: sources/storage-engines/wiredtiger/src/include/verbose.h

## Purpose

`verbose.h` defines WiredTiger's internal verbose logging convenience layer. It does not implement message formatting or dispatch itself; instead, it gives hot-path code cheap category/level checks and then calls the cold worker functions declared in `extern.h` and implemented in `src/support/err.c`. The header centralizes the mapping between `WT_VERBOSE_CATEGORY` / `WT_VERBOSE_LEVEL` values and the macros used throughout the storage engine to emit diagnostic messages.

The file also stores generated category string data with `WT_VERBOSE_CATEGORY_STR_INIT`. `src/support/err.c` uses this initializer for `verbose_category_strings[]`, and JSON verbose output includes those strings plus numeric category and level identifiers.

## Important APIs, Types, and Macros

`WT_VERBOSE_MESSAGE_INFO` bundles a log id, category, and level for id-bearing verbose messages. The id-aware macros create this structure on the stack and pass it to `__wt_verbose_worker_id`.

`WT_VERBOSE_MULTI_CATEGORY` stores a pointer to a category array plus its count. `WT_DECL_VERBOSE_MULTI_CATEGORY(items)` builds that structure with `WT_ELEMENTS(items)`, commonly from compound literals such as `((WT_VERBOSE_CATEGORY[]){WT_VERB_RECOVERY, WT_VERB_RTS})`.

`WT_VERBOSE_CATEGORY_STR_INIT` is a generated initializer whose order must match the public `WT_VERBOSE_CATEGORY` enum in `src/include/wiredtiger.h.in`. `__wt_verbose_category_string` returns these names for diagnostics and falls back to `"unknown"` only when the category is outside `WT_VERB_NUM_CATEGORIES`.

`WT_VERBOSE_LEVEL_STR(level, level_str)` maps `WT_VERBOSE_ERROR`, `WT_VERBOSE_WARNING`, `WT_VERBOSE_NOTICE`, `WT_VERBOSE_INFO`, and `WT_VERBOSE_DEBUG_1` through `WT_VERBOSE_DEBUG_5` to string labels used by event formatting.

`WT_SET_VERBOSE_LEVEL`, `WT_VERBOSE_LEVEL_ISSET`, and `WT_VERBOSE_ISSET` read and write `S2C(session)->verbose[category]` via relaxed enum atomics. `WT_VERBOSE_LEVEL_DEFAULT` is `WT_VERBOSE_DEBUG_1`, preserving the historical behavior of older category-only verbose messages. `WT_VERBOSE_CATEGORY_DEFAULT` is `WT_VERB_DEFAULT` and is used by generic error macros in `include/error.h`.

`WT_VERBOSE_SET_AND_SAVE` and `WT_VERBOSE_RESTORE` temporarily override one category's level and restore it from a caller-provided array. `src/support/generation.c` uses this near generation-drain timeouts to turn on extra eviction, reconciliation, and checkpoint logging.

The emission macros are `__wt_verbose_level`, `__wt_verbose_error`, `__wt_verbose_warning`, `__wt_verbose_notice`, `__wt_verbose_info`, `__wt_verbose_debug1`, `__wt_verbose_debug2`, `__wt_verbose_debug3`, and the legacy `__wt_verbose`. The id variants are `__wt_verbose_level_id` and `__wt_verbose_info_id`. The multi-category variants are `__wt_verbose_level_multi_id`, `__wt_verbose_level_multi`, and `__wt_verbose_multi`.

`WT_CONFIG_DEBUG` is a narrow helper that emits a configuration warning when `S2C(session)->debug.flags` contains `WT_CONN_DEBUG_CONFIGURATION`; it routes through the normal verbose warning path for `WT_VERB_CONFIGURATION`.

## Control Flow

The normal control path is: caller invokes a macro with a `WT_SESSION_IMPL *`, category, level, format string, and at least one variadic argument; the macro checks `WT_VERBOSE_LEVEL_ISSET`; only if the configured threshold allows the requested level does it call `__wt_verbose_worker` or `__wt_verbose_worker_id`. The worker functions in `support/err.c` create a `va_list` and call `__eventv`, which adds timestamp, thread id, optional session and dhandle context, category, log id, level, and the formatted message before sending it through the event handler or stderr fallback.

Level comparisons rely on the enum ordering from `wiredtiger.h.in`: `WT_VERBOSE_ERROR` is the most severe and has the lowest numeric value, while `WT_VERBOSE_DEBUG_5` is the most verbose. The predicate `(requested_level <= configured_level)` means a category configured at `NOTICE` receives error, warning, and notice messages, while a category configured at `DEBUG_2` also receives default/debug1 and debug2 messages.

Multi-category macros iterate categories in caller-provided order. `__wt_verbose_level_multi` and `__wt_verbose_multi` emit once for the first category whose configured level satisfies the request, then break. The id-bearing multi macro calls `__wt_verbose_level_id` for each category, so it may emit more than one message if multiple categories are enabled.

`__wt_verbose_level_multi` and `__wt_verbose_multi` first copy the `multi_category` expression into a local variable. The file comments call out why: callers may pass a ternary expression returning different category sets, and evaluating it repeatedly could select inconsistent sets.

## State and Persistence Behavior

This header creates no durable storage. Runtime verbose state lives in `WT_CONNECTION_IMPL.verbose[WT_VERB_NUM_CATEGORIES]`, declared in `include/connection.h`. `__wt_verbose_config` in `conn/conn_api.c` populates that array from the `verbose=[...]` connection configuration. If `all` is not present, unspecified categories default to `WT_VERBOSE_NOTICE`; if a category is present without a numeric value, it uses `WT_VERBOSE_LEVEL_DEFAULT`.

Verbose settings are process-local connection state and can be adjusted during connection setup and reconfiguration. The save/restore macros mutate the same array temporarily; callers must provide a correctly sized `WT_VERBOSE_LEVEL verbose_orig_level[WT_VERB_NUM_CATEGORIES]` and restore every category they saved.

Event messages themselves are not persisted by this header. They are passed to the configured event handler, JSON output path, stderr fallback, or error-log infrastructure depending on `support/err.c` and connection settings.

## Dependencies and Integration Points

The header depends on core WiredTiger typedefs and enums being available first: `WT_VERBOSE_CATEGORY`, `WT_VERBOSE_LEVEL`, `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, `WT_VERBOSE_MESSAGE_INFO`, and `WT_VERBOSE_MULTI_CATEGORY` are tied together through `wt_internal.h`, `wiredtiger.h.in`, and `connection.h`.

It integrates with `conn/conn_api.c` for verbose category names accepted in configuration. The config name table must stay consistent with `WT_VERBOSE_CATEGORY` and `WT_VERBOSE_CATEGORY_STR_INIT`.

It integrates with `support/err.c`, which owns `verbose_category_strings[]`, `__eventv`, `__wt_verbose_worker`, `__wt_verbose_worker_id`, and `__wt_verbose_category_string`.

It is used broadly by subsystems such as block manager, checkpoint, compaction, eviction, layered/disaggregated storage, recovery, rollback-to-stable, transaction, and version reporting. `btree/bt_handle.c` uses `WT_VERB_VERSION` to dump btree version information, while connection open emits the WiredTiger version string through the same category.

## Risks and Edge Cases

The generated string initializer is order-sensitive. Adding, removing, or reordering `WT_VERBOSE_CATEGORY` values without regenerating/updating `WT_VERBOSE_CATEGORY_STR_INIT` and the configuration mapping in `conn_api.c` can produce misleading category names or broken configuration behavior.

The variadic macros require at least one argument after the format string. The header explicitly documents that it does not use a non-portable empty `__VA_ARGS__` comma elision trick. Callers that only need a literal message usually pass `"%s", "message"`.

The macros assume `session` is valid for the pre-check because `WT_VERBOSE_LEVEL_ISSET` immediately evaluates `S2C(session)`. The worker can handle a null session, but the macro gate generally cannot.

Relaxed atomic access is appropriate for diagnostic thresholds but does not provide sequencing beyond atomicity. Code must not rely on verbose-level changes as synchronization for other state.

Save/restore is fragile if used with a partially initialized `verbose_orig_level` array or if error paths skip restore. That can leave extra diagnostic output enabled for a category longer than intended.

`WT_VERBOSE_LEVEL_STR` has no default case. Unknown level values leave the output string as `""`, so validation in `__wt_verbose_config` and direct macro callers are important.

The id multi-category macro can emit duplicate messages across categories, unlike the non-id multi macros that stop after the first enabled category. Callers need to choose the variant based on whether repeated category-tagged events are desirable.

## Test Signals

Python verbose tests such as `test/suite/test_verbose02.py` and `test/suite/test_verbose04.py` exercise category coverage and expected default `WT_VERBOSE_DEBUG_1` behavior. These are good regression signals when changing category lists, defaults, or config parsing.

Compile tests should catch missing enum labels used in `WT_VERBOSE_LEVEL_STR` and mismatches in category names if generated code is refreshed. Runtime tests should verify `verbose=[all:N]`, category-specific overrides, boolean category entries, invalid negative/string levels, and JSON output fields for category, category id, log id, and verbose level.

Call-site tests around generation-drain timeout logging can validate `WT_VERBOSE_SET_AND_SAVE` / `WT_VERBOSE_RESTORE` behavior by ensuring temporary debug categories are enabled only for the diagnostic window and are restored afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verbose.h -->
