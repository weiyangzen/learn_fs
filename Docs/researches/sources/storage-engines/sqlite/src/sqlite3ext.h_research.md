# sources/storage-engines/sqlite/src/sqlite3ext.h

## Purpose

`sqlite3ext.h` is SQLite's public-facing header for loadable extensions. Extensions include this header instead of `sqlite3.h` so that calls to SQLite APIs can be routed through a function-pointer table supplied by the SQLite library that loads the extension.

The file defines the loadable-extension ABI boundary:

- `struct sqlite3_api_routines`, a fixed-order table of SQLite C API function pointers.
- `sqlite3_loadext_entry`, the expected entry-point signature for dynamically loaded or automatically loaded extensions.
- Macro redirects that turn ordinary-looking calls such as `sqlite3_create_function()` into `sqlite3_api->create_function()` when compiling an extension.
- `SQLITE_EXTENSION_INIT1`, `SQLITE_EXTENSION_INIT2()`, and `SQLITE_EXTENSION_INIT3`, which declare and initialize the extension-local `sqlite3_api` pointer.

The header contains no runtime algorithm of its own. Its behavior is compile-time ABI setup. The implementation-side companion is `loadext.c`, which includes this header with `SQLITE_CORE` defined, builds the concrete `sqlite3Apis` table, and passes that table to extension entry points.

## Important APIs, Types, And Macros

The central type is `struct sqlite3_api_routines`. It contains more than 300 function-pointer slots, ordered by historical introduction. The warning at the top of the struct is critical: new interfaces must be appended to the end only. Inserting or reordering entries would break binary compatibility between SQLite libraries and separately compiled extensions.

Major API families exposed through the table include:

- Connection lifecycle and execution: `open`, `open16`, `open_v2`, `close`, `close_v2`, `exec`, `interruptx`, `db_handle`, `db_filename`, `db_name`, `db_readonly`, `db_config`, `db_status`, and `db_status64`.
- Prepared statements: `prepare`, `prepare_v2`, `prepare_v3`, UTF-16 variants, `step`, `reset`, `finalize`, `clear_bindings`, `expanded_sql`, `normalized_sql`, `stmt_busy`, `stmt_readonly`, `stmt_status`, `stmt_isexplain`, and `stmt_explain`.
- Parameter binding and value access: scalar bind APIs, 64-bit text/blob bind APIs, zeroblob APIs, pointer binding APIs, `value_*` accessors, value duplication/freeing, subtype APIs, encoding checks, and `value_frombind`.
- Result construction: `result_*` scalar/blob/text APIs, 64-bit result APIs, error reporting helpers, subtype and pointer result APIs, and zeroblob result APIs.
- User-defined SQL behavior: `create_function`, `create_function_v2`, `create_window_function`, collations, authorizers, hooks, aggregate context, auxdata, and user data.
- Virtual table support: `create_module`, `create_module_v2`, `declare_vtab`, `overload_function`, `vtab_config`, `vtab_on_conflict`, `vtab_nochange`, `vtab_collation`, `vtab_rhs_value`, `vtab_distinct`, `vtab_in`, `vtab_in_first`, `vtab_in_next`, and `drop_modules`.
- BLOB, backup, serialization, and file/VFS access: incremental blob APIs, backup APIs, `serialize`, `deserialize`, VFS registration/lookup, filename helpers, `file_control`, `create_filename`, `free_filename`, and `database_file_object`.
- Memory, mutex, and status APIs: SQLite allocators, `msize`, `release_memory`, heap limit APIs, mutex APIs, global/database/statement status APIs, `randomness`, `sleep`, and `threadsafe`.
- WAL, transaction, and hooks: commit/rollback/update hooks, WAL hook and checkpoint APIs, transaction state, auto-vacuum page callback, busy handler/timeouts, progress handler, trace/profile/trace_v2, unlock notification, and lock timeout.
- String and parser utilities: `mprintf`, `vmprintf`, snprintf wrappers, `stricmp`, `strnicmp`, `strglob`, `strlike`, keyword APIs, `sqlite3_str` builder APIs, `str_truncate`, `str_free`, `complete`, `incomplete`, URI parameter helpers, compile option queries, source ID, and version checks.
- Newer extension surfaces appended at the end include client data, per-connection error-message setting, carray binding helpers, and `sqlite3_incomplete()`.

`sqlite3_loadext_entry` is the canonical extension entry prototype:

```c
typedef int (*sqlite3_loadext_entry)(
  sqlite3 *db,
  char **pzErrMsg,
  const sqlite3_api_routines *pThunk
);
```

The macro redirect block is enabled only when neither `SQLITE_CORE` nor `SQLITE_OMIT_LOAD_EXTENSION` is defined. In that mode, most SQLite C API names are preprocessor aliases to fields of the global `sqlite3_api` pointer. Deprecated APIs are guarded by `SQLITE_OMIT_DEPRECATED`, and serialization macros are guarded by `SQLITE_OMIT_DESERIALIZE`.

The initialization macros have two modes:

- Loadable-extension mode: `SQLITE_EXTENSION_INIT1` defines `const sqlite3_api_routines *sqlite3_api=0;`, `SQLITE_EXTENSION_INIT2(v)` assigns the thunk received from SQLite, and `SQLITE_EXTENSION_INIT3` declares the global pointer for multi-file extensions.
- Core/static mode: the same macros compile to no-ops, or `(void)v`, so statically linked extension code can call SQLite APIs directly without thunk indirection.

## Control Flow

This header participates in extension loading through a simple compile-time/runtime handoff:

1. The extension source includes `sqlite3ext.h`, uses `SQLITE_EXTENSION_INIT1` at file scope, and defines an entry point with the `sqlite3_loadext_entry` shape.
2. SQLite's loader, implemented in `loadext.c`, opens the shared object or iterates automatic extension callbacks and calls the entry point with a database handle, an error-message pointer, and a `const sqlite3_api_routines *` thunk.
3. The extension entry point calls `SQLITE_EXTENSION_INIT2(pThunk)` before using SQLite APIs.
4. After initialization, calls written as normal SQLite C API names are macro-expanded to indirect calls through `sqlite3_api`.
5. When the same extension code is statically linked into the SQLite core, `SQLITE_CORE` suppresses macro redirects, and the API calls bind directly to core symbols.

There is no data-dependent control flow in the header beyond preprocessor conditionals. Compatibility is enforced by the positional layout of `sqlite3_api_routines`, not by runtime negotiation. Extensions that depend on newer slots are expected to use `sqlite3_libversion_number()` and null-pointer checks before calling recently added or optionally omitted APIs.

## State And Persistence Behavior

`sqlite3ext.h` does not persist database state. Its only stateful element is the extension-local `sqlite3_api` pointer declared by `SQLITE_EXTENSION_INIT1` in loadable-extension builds. That pointer is initialized from the `pThunk` argument supplied to the extension entry point and remains the dispatch table for the compiled extension module.

The APIs reachable through the table can mutate persistent SQLite state, including database files, WAL files, virtual table registrations, SQL functions, collations, hooks, blob handles, backup handles, and connection configuration. This header itself only exposes those operations; it does not own their storage or transaction semantics.

The ABI table is effectively persistent across binary builds in a different sense: the index of every slot is part of the extension binary contract. Appending entries preserves older binaries because the original offsets remain stable. Reordering, deleting, or inserting entries in the middle would cause compiled extensions to call the wrong SQLite functions.

## Dependencies And Integration Points

The header includes `sqlite3.h`, so all public SQLite types used in the function table are available: `sqlite3`, `sqlite3_stmt`, `sqlite3_context`, `sqlite3_value`, `sqlite3_blob`, `sqlite3_backup`, `sqlite3_module`, `sqlite3_vfs`, `sqlite3_file`, `sqlite3_mutex`, `sqlite3_str`, `sqlite3_index_info`, integer typedefs, callbacks, and public constants.

Important integration points in this source tree are:

- `loadext.c`: defines `SQLITE_CORE` before including `sqlite3ext.h`, builds `static const sqlite3_api_routines sqlite3Apis`, substitutes null pointers for APIs omitted by compile-time options, and passes `&sqlite3Apis` into loadable and automatic extension entry points.
- `sqlite.h.in`: declares `typedef struct sqlite3_api_routines sqlite3_api_routines;` as an opaque public type and documents the extension entry-point thunk in public API comments.
- Test and extension-like files such as `test_autoext.c`, `test_loadext.c`, `test_schema.c`, `test_md5.c`, and `test_multiplex.c`: include this header to validate automatic extension loading, load-extension behavior, statically linked extension patterns, and core-build macro suppression.
- Extension entry points registered from `test1.c`: use the `sqlite3*, char **, const sqlite3_api_routines*` signature to initialize bundled extensions through the same contract.

The compile-time feature macros are also integration points. `SQLITE_OMIT_LOAD_EXTENSION` disables the redirect block and changes extension-thunk availability. `SQLITE_CORE` lets SQLite core code see the struct definition without rewriting API names. `SQLITE_OMIT_DEPRECATED` and `SQLITE_OMIT_DESERIALIZE` selectively suppress some macros even when fields remain in the ABI table.

## Risks And Edge Cases

The highest-risk part of this file is ABI layout. The order of `sqlite3_api_routines` must match the initializer in `loadext.c` exactly. A mismatch compiles cleanly but causes runtime calls through the wrong function pointer, which can lead to memory corruption, incorrect database writes, or immediate crashes.

Version skew is expected. An extension compiled against a newer `sqlite3ext.h` may be loaded by an older SQLite library whose thunk does not contain newer tail entries. Correct extensions need to check `sqlite3_libversion_number()` before using newer APIs and should handle null function pointers for APIs omitted from a particular build.

Feature-omitted builds can expose null slots. `loadext.c` explicitly maps unavailable APIs such as UTF-16 support, column metadata, authorization, virtual tables, shared cache, tracing, get-table helpers, and incremental blob support to null in some builds. Extension code must not assume every macro target is callable.

Macro redirection can surprise code that takes addresses, defines wrappers, or mixes static and loadable extension modes. The same source compiles differently depending on `SQLITE_CORE` and `SQLITE_OMIT_LOAD_EXTENSION`, so extension code should keep `SQLITE_EXTENSION_INIT*` usage conventional and avoid defining conflicting `sqlite3_*` symbols.

Initialization order matters. If a loadable extension calls any redirected SQLite API before `SQLITE_EXTENSION_INIT2(pThunk)`, it dereferences a null `sqlite3_api` pointer. Multi-file extensions need exactly one definition via `SQLITE_EXTENSION_INIT1` and external declarations via `SQLITE_EXTENSION_INIT3` in other translation units.

Deprecated and historical aliases need care. The table retains slots for older APIs such as `aggregate_count`, `expired`, `global_recover`, `profile`, `trace`, and `transfer_bindings` to preserve offsets, but modern builds may replace some with null pointers or hide macros behind `SQLITE_OMIT_DEPRECATED`.

## Test Signals

Good coverage for this header comes from extension loading and ABI-compatibility tests rather than direct unit tests of control flow. Useful signals include:

- Build a simple loadable extension that uses `SQLITE_EXTENSION_INIT1`, calls `SQLITE_EXTENSION_INIT2()`, registers a scalar function with `sqlite3_create_function()`, and verifies that redirected API calls succeed after `sqlite3_load_extension()`.
- Build the same extension source statically with `SQLITE_CORE` and verify the initialization macros become harmless no-ops and direct SQLite API calls still link.
- Exercise automatic extensions through `sqlite3_auto_extension()` and confirm SQLite passes the same thunk signature to callbacks opened on new database connections.
- Compile with feature omissions such as `SQLITE_OMIT_UTF16`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTHORIZATION`, `SQLITE_OMIT_INCRBLOB`, and `SQLITE_OMIT_LOAD_EXTENSION` to verify null-slot and macro-guard behavior.
- Load an extension compiled against newer headers into an older or reduced SQLite library and verify that version checks and null checks prevent calls through unavailable tail slots.
- Run tests that register functions, collations, virtual tables, hooks, blob handles, backup operations, WAL hooks, `sqlite3_str` builders, and pointer/subtype APIs from extension code, because each family validates a different region of the thunk table.
- Add ABI guard checks that compare the order of fields in `sqlite3_api_routines` with the initializer order in `loadext.c`, especially when appending new public APIs.
- Include negative tests for missing `SQLITE_EXTENSION_INIT2()`, duplicate `sqlite3_api` definitions across multi-file extensions, and use of deprecated APIs under `SQLITE_OMIT_DEPRECATED`.
