# sources/storage-engines/sqlite/ext/misc/completion.c

## Purpose

`completion.c` implements the eponymous virtual table `completion`, used to suggest completions for partial SQL input. It returns candidate keywords and schema identifiers, optionally filtered by hidden `prefix` and informed by hidden `wholeline`.

## Important APIs, types, and functions

`sqlite3_completion_init()` calls `sqlite3CompletionVtabInit()`, which registers `completion`. `completion_vtab` stores the SQLite connection. `completion_cursor` stores prefix/whole-line buffers, current candidate text, an active metadata statement, rowid, current phase, and a phase-local counter.

`completionModule` implements `xConnect`, `xBestIndex`, `xOpen`, `xFilter`, `xNext`, `xColumn`, `xRowid`, and cleanup. The table schema is `candidate TEXT, prefix HIDDEN, wholeline HIDDEN, phase HIDDEN`. The module is marked `SQLITE_VTAB_INNOCUOUS`.

## Control flow

`completionBestIndex()` finds equality constraints on `prefix` and `wholeline`, assigns argv positions, omits the hidden constraints, and lowers estimated cost/rows when arguments are supplied. `completionFilter()` copies the prefix and/or whole line into cursor-owned memory. If only `wholeline` is provided, it derives the prefix from the trailing alphanumeric or underscore token. It starts at `COMPLETION_FIRST_PHASE` and calls `completionNext()`.

`completionNext()` advances through phases. It enumerates `sqlite3_keyword_name()` results, then `PRAGMA database_list`, then table/view/trigger names from each attached database's `sqlite_schema`, then column names from `pragma_table_xinfo()` joined to schema rows. Prepared statements are finalized at phase boundaries. Each candidate is case-insensitively compared to `zPrefix`; nonmatching candidates are skipped.

## State and persistence

The module is read-only and holds no persistent state. Cursor state includes copied input strings and one active prepared statement at a time. It queries SQLite metadata dynamically, so attached databases and schema changes affect later scans.

## Dependencies and integration points

It depends on SQLite keyword APIs, pragma table-valued functions, `sqlite3_str` construction, attached database metadata, and virtual table planning. It is intended for interactive shell completion and may return duplicates; callers are expected to use `DISTINCT` and ordering when needed.

## Risks

`wholeline` is currently used only to derive a trailing prefix, not to restrict suggestions to syntactically valid positions. Metadata SQL spans attached databases, so prepare/finalize errors from one database can abort the scan. Candidate lifetime is mixed: keyword names are static, metadata values are copied out with `SQLITE_TRANSIENT` in `xColumn`. Duplicate names are normal behavior.

## Test signals

Tests should verify prefix filtering for keywords and object names, prefix derivation from `wholeline`, rowid monotonicity, phase visibility, behavior with attached databases, duplicate handling by caller queries, and clean EOF when there are no matching candidates.
