<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_tool.c -->
# sources/user-network-fs/samba/source3/utils/dbwrap_tool.c

## Purpose
`dbwrap_tool.c` is a low-level command-line tool for inspecting and mutating Samba dbwrap/TDB databases. It supports typed fetch/store, delete, existence checks, wiping a database, and listing keys.

## Important APIs, types, and functions
- `enum dbwrap_op` and `enum dbwrap_type` classify supported operations and data encodings.
- Fetch/store helpers handle `int32`, `uint32`, NUL-terminated `string`, and `hex` data via dbwrap typed helpers or raw `TDB_DATA`.
- `dbwrap_tool_delete()`, `dbwrap_tool_exists()`, `dbwrap_tool_erase()`, and `dbwrap_tool_listkeys()` perform non-typed operations.
- `listkey_fn()` prints keys with printable bytes preserved and other bytes backslash-escaped as hex.
- `dispatch_table` maps operation/type pairs to implementation functions.
- `main()` parses `--persistent`/`--non-persistent`, validates operands, opens the database, and dispatches.

## Control flow
The program initializes Samba command-line context with log level 0, parses options, requires exactly one persistence mode, validates the operation-specific positional arguments, parses the requested type, initializes tevent and messaging, opens the named db with `db_open()`, and runs the matching dispatch entry. Persistent databases use transaction-aware store/delete helpers; non-persistent mode adds `TDB_CLEAR_IF_FIRST`, which may wipe data.

## State and persistence behavior
The target database is opened read/write with create mode `0644`. Store/delete/erase mutate it; fetch/list/exists read it. Non-persistent mode can clear the database when first opened, as warned by the option description. Hex store converts a string to binary data; string store writes a terminating NUL.

## Dependencies and integration points
The tool depends on dbwrap/dbwrap_open, util_tdb typed helpers, Samba command-line and loadparm context, messaging setup, talloc, tevent, popt, and data-blob hex helpers. It is useful for debugging Samba private and lock databases outside their owning daemons.

## Risks and edge cases
- `--non-persistent` may wipe the database because of `TDB_CLEAR_IF_FIRST`.
- Numeric parsing uses `strtol` without strict validation of trailing characters or range.
- `OP_DELETE`, `OP_ERASE`, and `OP_LISTKEYS` are registered only with `TYPE_INT32`, so user-specified alternate types will not dispatch.
- `exists` returns process status 1 when a key is absent, which is useful for scripts but different from operational failure.

## Test signals
Smoke tests can create a temporary db, store/fetch each type, list escaped keys, check exists exit codes, delete keys, and erase the db. Persistent mode should preserve records across invocations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_tool.c -->
