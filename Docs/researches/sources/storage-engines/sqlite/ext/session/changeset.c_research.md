# sources/storage-engines/sqlite/ext/session/changeset.c

## Purpose
`changeset.c` implements a standalone command-line utility for inspecting, transforming, and applying SQLite session extension changeset blobs. It is a developer/test tool around the `sqlite3changeset_*` APIs rather than a library component.

## Important APIs, Types, And Functions
`usage()` prints supported commands. `readFile()` reads an entire changeset file into SQLite-allocated memory. `renderValue()` formats `sqlite3_value` objects as SQL-ish literals for dumps and pseudo-SQL output. `conflictCallback()` formats apply conflicts and returns `SQLITE_CHANGESET_OMIT`.

The `main()` command dispatcher supports:
`apply DB [OPTIONS]` to apply a changeset to a database;
`concat FILE2 OUT` to concatenate two changesets;
`dump` to print detailed changeset contents;
`invert OUT` to write an inverted changeset;
`sql` to print pseudo-SQL representing the changeset.

The file exercises session APIs including `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2()`, `sqlite3changeset_concat()`, `sqlite3changeset_invert()`, `sqlite3changeset_start()`, `sqlite3changeset_next()`, `sqlite3changeset_finalize()`, `sqlite3changeset_op()`, `sqlite3changeset_pk()`, `sqlite3changeset_old()`, and `sqlite3changeset_new()`.

## Control Flow
Startup requires at least a file and command. The input changeset is read before command dispatch. `apply` parses flags, opens the target database, optionally enables foreign keys, begins a transaction, applies the changeset with conflict handling, and commits only if there are no conflicts, no dry-run request, and no apply error.

`concat` reads a second file, calls `sqlite3changeset_concat()`, and writes the output. `invert` calls `sqlite3changeset_invert()` and writes the result. `dump` iterates through changes, prints operation metadata, primary-key flags, and old/new values. `sql` iterates through changes and emits a simple transaction containing DELETE, UPDATE, or INSERT statements with synthetic column names `c1`, `c2`, and so on.

## State And Persistence Behavior
The tool keeps the input and generated changesets in memory. `apply` is the only command that mutates a database, and it wraps the operation in an explicit transaction. Conflicts, dry-run mode, and apply errors cause rollback. `concat` and `invert` overwrite their output file if opened successfully.

`nConflict` is a process-global counter reset before apply. Conflict handling always returns omit, leaving final commit/rollback policy to `main()`.

## Dependencies
The file depends on SQLite with the session extension APIs enabled, standard C file IO, string handling, ctype, and assertions. It relies on SQLite memory allocation for buffers returned by changeset APIs.

## Integration Points
This utility is useful in session extension tests and debugging pipelines. It can render changesets for human inspection, combine generated changesets, invert them for undo-style testing, and apply them to fixture databases while exposing conflict diagnostics.

## Risks And Edge Cases
`readFile()` stores file size in `sqlite3_int64` but returns it through `int`, so very large files can truncate. It only closes the file on successful non-empty reads; empty files and read-error exits do not consistently close before exit, though process termination masks most leaks.

The `apply` option parser normalizes long options by skipping one leading dash, so both `--invert` and `-invert` work, but unsupported spellings fail. Pseudo-SQL output is diagnostic only: column names are synthetic, table quoting is simple, and values are rendered for readability rather than guaranteed replay across all schemas.

`renderValue()` iterates text byte-by-byte and only doubles single quotes; it does not attempt full SQL encoding for all encodings. Conflict handling always omits conflicting changes, so `apply` with conflicts never partially commits because the wrapper rolls back when `nConflict` is non-zero.

## Test Signals
Tests should cover all commands, output file failures, invalid changesets, apply flags (`--dryrun`, `--enablefk`, `--nosavepoint`, `--invert`, `--ignorenoop`, `--fknoaction`), conflict classes, old/new value rendering for NULL, integer, float, text with quotes, and blobs. Transaction tests should verify rollback on conflict and dry-run and commit on clean apply.
