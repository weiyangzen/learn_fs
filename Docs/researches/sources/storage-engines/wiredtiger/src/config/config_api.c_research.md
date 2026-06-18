# sources/storage-engines/wiredtiger/src/config/config_api.c

## Purpose

`config_api.c` is the public and connection-facing API layer for WiredTiger configuration parsing and extensible configuration definitions. It provides the `wiredtiger_config_parser_open` public helper, the `wiredtiger_config_validate` public validation helper, connection lifetime cleanup for dynamically allocated configuration metadata, and `__wt_configure_method`, which lets extensions add or override configuration options on existing API methods.

The file is deliberately thin around parsing itself: iteration and lookup are delegated to the core config parser helpers, while validation is delegated to `__wt_config_check`. Its main responsibilities are object lifetime, entry lookup, event-handler setup for standalone validation, and atomic replacement of connection configuration entries.

## Important APIs, Types, and Functions

`wiredtiger_config_parser_open(WT_SESSION *, const char *, size_t, WT_CONFIG_PARSER **)` allocates a `WT_CONFIG_PARSER_IMPL`, installs a static method table, stores the session, initializes both a `WT_CONFIG_ITEM` for lookup and a `WT_CONFIG` iterator for sequential traversal, and returns it as the public `WT_CONFIG_PARSER`.

`__config_parser_close`, `__config_parser_next`, and `__config_parser_get` implement the public parser methods. `close` frees the implementation via the stored session, `next` calls `__wt_config_next`, and `get` calls `__wt_config_subgets` against the whole saved config item.

`wiredtiger_config_validate` calls the private `__config_validate` wrapper with `__wt_conn_config_match`, so it validates a supplied config string against a named WiredTiger API’s generated configuration entry.

`__config_validate` accepts either a real session or an event handler, rejects the invalid combination of both, creates a minimal dummy connection/session when only an event handler is supplied, resolves the named `WT_CONFIG_ENTRY`, and invokes `__wt_config_check`.

`__wt_configure_method` implements `WT_CONNECTION.configure_method`. It appends a new default setting to an existing method’s base config, creates a replacement `WT_CONFIG_CHECK` array with one new or replacement check, validates the supplied config under the new rules, stores all newly allocated memory on the connection free-on-close list, and atomically publishes the new `WT_CONFIG_ENTRY *`.

`__config_add_checks` parses a check string such as `min=...`, `max=...`, and `choices=...` into the runtime fields on `WT_CONFIG_CHECK`: `min_value`, `max_value`, and a NULL-terminated `choices` array. For structured choice lists it enumerates each element and duplicates the raw choice strings.

`__conn_foc_add` and `__wt_conn_foc_discard` maintain and drain `WT_CONNECTION_IMPL::foc`, the connection-level free-on-close list used for dynamically installed configuration metadata.

The key types come from `src/include/config.h`: `WT_CONFIG_PARSER_IMPL` contains the public interface, `WT_SESSION_IMPL *`, `WT_CONFIG`, and `WT_CONFIG_ITEM`; `WT_CONFIG_ENTRY` names a method, base config string, generated check table, jump table, and compile metadata; `WT_CONFIG_CHECK` describes a single allowed key, including compiled type, optional checker callback, subconfig table, min/max bounds, and choices.

## Control Flow

Parser creation is linear: set output to `NULL`, cast the public session to `WT_SESSION_IMPL *`, allocate one parser, assign the static vtable, copy a bounded `WT_CONFIG_ITEM`, initialize a bounded `WT_CONFIG`, then publish the result. Later `next` advances the iterator, while `get` searches within the saved item without mutating the iterator state.

Validation first establishes an error-reporting context. With a real session it uses the connection attached to that session. With only an event handler it fabricates enough `WT_CONNECTION_IMPL` and `WT_SESSION_IMPL` state to route messages through `__wt_event_handler_set`. Then it requires non-NULL `name` and `config`, looks up the method either in static generated entries or the connection’s mutable `config_entries`, and finally calls `__wt_config_check`.

`__config_add_checks` initializes broad numeric bounds, iterates over the `check` descriptor string, and handles three recognized keys. `min` and `max` are parsed with `strtoll` and require the whole config value to be numeric. `choices` requires a value; if the value is a struct it first counts elements, allocates `count + 1` pointers, then duplicates each raw element; otherwise it allocates two pointers and stores one duplicated choice. Choice strings and the choice pointer array are registered for connection-close cleanup.

`__wt_configure_method` validates arguments and maps user-facing type strings to compiled type constants. It finds the target method in `conn->config_entries`, takes `conn->api_lock`, allocates a replacement entry, builds a new base string as `old_base,new_config`, extracts the new key name by truncating at `=`, copies all existing checks except a replaced key of the same name, fills the new check, validates the new config against the new entry, adds all allocated chunks to the free-on-close list, and publishes with `WT_RELEASE_WRITE_WITH_BARRIER`. Error cleanup is local until ownership is transferred to the free-on-close list.

## State and Persistence Behavior

The parser object owns only its small implementation allocation. It does not copy the input config string; both the `WT_CONFIG_ITEM` and iterator point at caller-provided memory. Callers must keep the config bytes alive until the parser is closed.

`wiredtiger_config_validate` has no durable side effects. The dummy connection path is stack-backed and exists solely for event dispatch during a standalone validation call.

`__wt_configure_method` mutates live connection state by replacing one pointer in `conn->config_entries`. Old and new configuration metadata can remain reachable by lock-free readers, so old dynamically allocated objects are intentionally retained until connection close. The free-on-close list is therefore a connection-lifetime persistence mechanism for memory, not on-disk configuration. The new base config influences future API config defaults and validation for the lifetime of the connection.

The source file has one surprising runtime side effect: `__config_add_checks` writes `entry->method` and `cp->name` to `stderr`. If this is compiled into normal builds, configuring methods may emit unexpected output outside WiredTiger’s event system.

## Dependencies and Integration Points

This file depends on `wt_internal.h` for allocation (`__wt_calloc_one`, `__wt_calloc_def`, `__wt_strdup`, `__wt_strndup`, `__wt_free`), parser initialization and traversal (`__wt_config_init`, `__wt_config_initn`, `__wt_config_subinit`, `__wt_config_next`, `__wt_config_subgets`, `__wt_config_subgetraw`), error macros, spin locks, connection access (`S2C`), and release-store barriers.

It integrates with generated config definitions in `config_def.c`. `__wt_conn_config_init` copies static `config_entries` into `conn->config_entries`, and `__wt_conn_config_match` searches the static list for validation without a live connection. `__wt_configure_method` updates the connection copy.

It integrates with `config_check.c` through `__wt_config_check`, which consumes the `WT_CONFIG_ENTRY` and `WT_CONFIG_CHECK` structures prepared or selected here.

Public integration points are declared in `wiredtiger.h.in`: applications and tests use `wiredtiger_config_parser_open` and `wiredtiger_config_validate`; extensions reach parser helpers through `config_ext.c`; tests in `test/csuite/config/main.c` and `test/cppsuite/src/main/configuration.cpp` create parsers over full and nested config strings.

## Risks and Edge Cases

The parser borrows config memory. Passing a temporary buffer and using the parser after the buffer is freed will produce invalid reads.

`__config_validate` rejects supplying both a session and an event handler because the handler would be ignored. Callers expecting the passed handler to override session behavior will get `EINVAL`.

`__wt_configure_method` intentionally ignores `uri`, so added options become valid for the entire method rather than a specific data source. This can mask misspelled or unsupported options for implementations that do not consume them.

`__conn_foc_add` ignores allocation failures. If the free-on-close list cannot grow, dynamically allocated config metadata can leak. The code comments accept this because `configure_method` is rare.

`__wt_configure_method` depends on pointer-sized atomic publication and connection-close cleanup to avoid locking readers. Any future change that frees old entries earlier would risk use-after-free by lock-free config readers.

`__config_add_checks` does not reject unknown check-string keys; it silently ignores anything except `min`, `max`, and `choices`. If a caller misspells a check directive, validation may be weaker than intended.

The `fprintf(stderr, ...)` in `__config_add_checks` is a behavioral risk for libraries and tests that expect no direct stderr output.

`__wt_strdup(session, check, &newcheck->checks)` is called after `newcheck->checks = check`; if the public `check` argument is optional and passed as `NULL`, this relies on `__wt_strdup` accepting NULL or will fail/crash depending on allocator helper semantics. The validation path handles `checks == NULL`, but the duplication call should be considered when changing API contracts.

## Test Signals

Existing parser behavior is exercised by `test/csuite/config/main.c`, which opens parsers, iterates config entries, recursively parses structs, and compares compiled config results against parser lookups. `test/cppsuite/src/main/configuration.cpp` also opens parsers for full and nested configs.

Useful targeted tests for this file include parser lifetime and NULL-output behavior, validation with session-only, event-handler-only, and invalid session-plus-handler inputs, unknown API name errors, `configure_method` replacement of an existing key, choice/min/max validation for dynamically added keys, and verification that dynamically configured methods continue to validate correctly after concurrent readers observe either the old or new entry.

Tests should also cover direct extension-facing use through `config_ext.c`, because extension parser wrappers delegate to `wiredtiger_config_parser_open`.
