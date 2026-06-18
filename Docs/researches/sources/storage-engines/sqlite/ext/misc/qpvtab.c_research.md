# sources/storage-engines/sqlite/ext/misc/qpvtab.c

Purpose: implements `qpvtab`, a planner-debug virtual table that reports the `sqlite3_index_info` content seen by `xBestIndex()`.

Important APIs/types/functions: `qpvtab_cursor` scans generated diagnostic text. `qpvtabBestIndex()` builds `idxStr`, calls `sqlite3_vtab_rhs_value()`, sets argv/omit usage, and records order/distinct/colUsed/idx flags. `qpvtabColumn()` parses diagnostic rows and emits synthetic `a`-`e` values.

Control flow: planning records all constraints and order-by entries, with hidden `flags` controlling integer output, `orderByConsumed`, and LIMIT/OFFSET omission. Filtering receives the generated `idxStr` and scans newline-delimited rows.

State and persistence: allocated `idxStr` is freed by SQLite; cursor state is transient.

Dependencies/integration: SQLite virtual table planner APIs, especially RHS-value and distinct introspection.

Risks/test signals: diagnostic format is CSV-like and version-sensitive; RHS values with commas/newlines may be lossy. Test equality/range/blob/text/null RHS values, LIMIT/OFFSET, order-by consumption, `colUsed`, rowid constraints, and flag-controlled behavior.
