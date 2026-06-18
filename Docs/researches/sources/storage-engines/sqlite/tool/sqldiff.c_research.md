# sources/storage-engines/sqlite/tool/sqldiff.c

## Purpose

Command-line SQLite database differ. It compares DB1 to DB2 and emits SQL that transforms DB1 into DB2, or alternative outputs such as summaries, RBU data tables, or binary changesets.

## Important APIs, control flow, and dependencies

Global `g` carries options, debug flags, schema-compare state, and the main SQLite connection with DB2 attached as `aux`. Error and preparation helpers include `cmdlineError()`, `runtimeError()`, `safeId()`, `db_prepare()`, and `namelistFree()`. `columnNames()` discovers primary-key columns, rowid accessibility, schema-defined versus true primary keys, and special `sqlite_schema` comparison keys. `printQuoted()` formats SQLite values as SQL literals. `dump_table()` recreates tables and rows from `aux`; `diff_one_table()` builds a compound SELECT for changed, deleted, and inserted rows and emits DDL/DML. `checkSchemasMatch()` gates RBU and changeset modes. RBU support uses Fossil delta helpers (`hash_*`, `putInt()`, `checksum()`, `rbuDeltaCreate()`), `getRbudiffQuery()`, and `rbudiff_one_table()`. Summary mode is `summarize_one_table()`. Changeset mode uses `putsVarint()`, `putValue()`, and `changeset_one_table()` to write SQLite changeset-like binary records. Virtual table filtering is handled by `module_name_func()` and `all_tables_sql()`. `main()` parses options, loads extensions, opens and attaches databases read-only, optionally wraps SQL output in a transaction, chooses the diff callback, and iterates selected tables.

## State, persistence, and integration

The input databases are opened read-only. Text SQL modes write to stdout unless `--changeset FILE` opens a binary output file. `--rbu` emits SQL to populate RBU tables and an `rbu_count` table. `--changeset` disables transaction wrapping. `--lib` enables extension loading so virtual table modules or custom collations can be available during comparison. The tool intentionally does not handle trigger or view differences, as noted at the end of `main()`.

## Risks and test signals

Risks include primary-key inference edge cases, inaccessible rowids, schema mismatches causing drop/recreate output, virtual table shadow-table filtering mistakes, control-character SQL literal formatting, binary changeset compatibility, and RBU delta generation for blobs. Large tables can be expensive because comparisons are SQL joins ordered by primary key. Test signals include fixture pairs for inserts/updates/deletes, WITHOUT ROWID and INTEGER PRIMARY KEY tables, hidden rowid-name conflicts, `sqlite_schema` comparisons, virtual tables with `--vtab`, extension loading, `--summary`, `--rbu`, `--changeset`, and applying emitted SQL to DB1 then comparing against DB2.
