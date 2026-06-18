# sources/storage-engines/sqlite/src/prepare.c

## Purpose
`prepare.c` implements SQLite's statement preparation APIs and schema-loading path. It is responsible for converting SQL text into VDBE statements, loading `sqlite_schema` rows into in-memory `Table`, `Index`, `Trigger`, and `View` structures, validating schema cookies, retrying after schema changes, and exposing the public UTF-8 and UTF-16 `sqlite3_prepare*()` entry points.

The file sits between the public API, the Lemon parser, the btree schema tables, and VDBE lifecycle. It is also used recursively while schema rows are being loaded: stored `CREATE` SQL is prepared while `db->init.busy` is set so the parser builds metadata without running the DDL.

## Important APIs, Types, and Functions
`sqlite3InitCallback()` is the callback used by `sqlite3_exec()` over `sqlite_schema`. It validates each schema row, prepares stored `CREATE` SQL, records root page numbers for implicit indexes, and reports malformed schema errors through `InitData`.

`sqlite3InitOne(sqlite3*, int, char**, u32)` initializes one database schema. It constructs the built-in schema table, opens a read transaction if needed, reads btree metadata cookies, validates text encoding and file format, applies default cache size, scans `sqlite_schema`, loads analysis statistics, and marks `DB_SchemaLoaded` on success. `sqlite3Init()` initializes main first, then attached schemas, then temp last. `sqlite3ReadSchema(Parse*)` is the parser-facing wrapper that records parse errors.

`schemaIsValid(Parse*)` checks btree schema cookies against cached schema cookies and resets stale schemas. `sqlite3SchemaToIndex()` maps a `Schema*` back to `db->aDb[]` index. `sqlite3IndexHasDuplicateRootPage()` detects corrupt schemas where sibling indexes share a root page.

Parser lifetime helpers include `sqlite3ParseObjectInit()`, `sqlite3ParseObjectReset()`, and `sqlite3ParserAddCleanup()`. These manage the active `db->pParse` chain, lookaside-disable counters, labels, table locks, constant expressions, trigger programs, and uncommon cleanup callbacks.

`sqlite3Prepare()` is the internal compiler. `sqlite3LockAndPrepare()` wraps it with API validation, connection mutex, all-btree mutex entry, schema-change retry, API-exit normalization, and busy-handler reset. `sqlite3Reprepare()` recompiles saved-SQL statements after schema change and swaps the new VDBE into the old handle. Public APIs are `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, and, when UTF-16 is enabled, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, and `sqlite3_prepare16_v3()`.

## Control Flow
Schema loading starts in `sqlite3Init()`. The main database schema is initialized first because it fixes the connection text encoding; attached schemas follow in reverse index order, with temp last. `sqlite3InitOne()` synthesizes a `CREATE TABLE x(type text,name text,tbl_name text,rootpage int,sql text)` row for `sqlite_schema`/`sqlite_temp_schema` and passes it through `sqlite3InitCallback()` so the parser owns schema-table construction too.

For disk-backed schemas, `sqlite3InitOne()` enters the btree mutex, begins a read transaction if none exists, reads btree meta values, applies reset-database behavior, sets schema cookie, validates encoding compatibility, initializes cache size, checks file format, clears legacy file format for modern main databases, then runs `SELECT * FROM "<schema>".sqlite_schema ORDER BY rowid`. The authorizer is disabled during this internal scan. Each row is routed to `sqlite3InitCallback()`.

`sqlite3InitCallback()` rejects missing rootpage fields, validates rootpage integers when extra schema checks are enabled, and only prepares schema SQL that begins with `CREATE` by checking the first two letters. While `db->init.busy` is set, `sqlite3Prepare()` parses DDL into schema objects without executing VDBE bytecode. Blank SQL rows represent implicit PRIMARY KEY/UNIQUE indexes; the callback finds the existing `Index`, records its root page, and checks for invalid or duplicate root pages.

Statement preparation through the public API enters `sqlite3LockAndPrepare()`. It validates `ppStmt`, database handle, and SQL pointer, takes the database mutex, enters all btrees, and calls `sqlite3Prepare()` repeatedly for transient `SQLITE_ERROR_RETRY` or once after `SQLITE_SCHEMA` with a full schema reset. The retry loop is bounded by `SQLITE_MAX_PREPARE_RETRY`.

`sqlite3Prepare()` creates a stack `Parse`, links it into `db->pParse`, optionally sets reprepare/explain state, disables lookaside for persistent statements, checks schema locks in shared-cache mode, unlocks pending virtual-table disconnects, copies non-nul-terminated SQL slices when needed, runs the parser, returns the tail pointer, stores original SQL text on non-schema-loading VDBEs, validates schema if parser requested it after an error, finalizes failed VDBEs, transfers error messages to the database handle, frees trigger programs, and resets the `Parse` object.

UTF-16 prepare first normalizes the byte count to a complete UTF-16 string, converts to UTF-8 under the connection mutex, calls `sqlite3LockAndPrepare()`, then maps the UTF-8 tail pointer back to a UTF-16 byte offset by counting UTF-8 characters and UTF-16 bytes.

## State and Persistence Behavior
This file does not directly modify user table contents, but it controls persistent-schema interpretation. It reads header metadata including schema cookie, file format, cache size, largest root page, and text encoding. It updates in-memory schema fields such as `schema_cookie`, `enc`, `cache_size`, `file_format`, table/index root pages, loaded-statistics state, and `DB_SchemaLoaded`.

Schema-loading state is stored in `db->init`: `busy`, `iDb`, `newTnum`, `orphanTrigger`, and `azInit`. `busy==1` means schema scan; `busy==2` is used for stricter ALTER TABLE ADD COLUMN parsing. `DBFLAG_EncodingFixed`, `DBFLAG_SchemaKnownOk`, `DBFLAG_SchemaChange`, `SQLITE_NoSchemaError`, `SQLITE_ResetDatabase`, `SQLITE_WriteSchema`, and `SQLITE_LegacyFileFmt` all alter behavior.

Preparation state is transient but critical. `Parse` owns labels, cleanup callbacks, locks, constant expressions, trigger programs, error text, VDBE pointer, tail pointer, and lookaside-disable count. `sqlite3ParseObjectReset()` restores the outer parse pointer and lookaside sizing, so every prepare path must reach it. Successful `prepare_v2/v3` stores SQL text in the VDBE for later automatic reprepare; legacy `sqlite3_prepare()` does not.

`sqlite3Reprepare()` preserves statement identity by compiling a fresh VDBE, swapping it into the existing one, transferring bindings, resetting step result state, and finalizing the temporary VDBE. This makes schema-change recovery visible as continuation of the original statement handle.

## Dependencies and Integration Points
`prepare.c` depends on the parser (`sqlite3RunParser()`), VDBE lifecycle (`sqlite3VdbeSetSql()`, finalize/swap/reset helpers), btree transactions and schema mutexes, schema hash structures, SQLite memory APIs, UTF conversion helpers, authorization hooks, virtual-table unlock handling, analysis-stat loading, and the public API exit/error normalization layer.

It is called by many subsystems that need schema availability through `sqlite3ReadSchema()`. `pragma.c` depends on that for schema-sensitive pragmas. Schema DDL execution depends back on `prepare.c` because parsing stored DDL creates in-memory objects. VDBE execution can invoke schema parsing through `OP_ParseSchema`, which also uses `sqlite3InitCallback()`.

The all-btree mutex discipline in `sqlite3LockAndPrepare()` is the concurrency boundary that makes schema-lock checks reliable. Shared-cache schema locks, schema cookies, and `sqlite3ResetOneSchema()` combine to prevent compiling statements against uncommitted or stale schema definitions.

## Risks and Edge Cases
Schema parsing is security- and corruption-sensitive. Malformed `sqlite_schema` rows can contain arbitrary text, so the callback only accepts SQL beginning with `CREATE` and treats other nonblank SQL as corruption. `SQLITE_WriteSchema` and `SQLITE_NoSchemaError` intentionally weaken normal corruption handling for recovery workflows and must not leak into ordinary prepare behavior.

Root-page validation has compatibility nuance. Some invalid root pages only become hard errors when `sqlite3Config.bExtraSchemaChecks` is enabled, while duplicate sibling index roots are always detected in that validation path. Reset-database mode zeros metadata and can bypass normal file state. Attached databases must match the main database encoding.

The prepare retry loop must distinguish transient parser retries, stale schema, OOM, locked schema, and permanent errors. Retrying too often risks hiding real errors; retrying too little breaks automatic schema-change recovery. The special `SQLITE_SCHEMA` branch resets all schemas only for the first schema failure.

Memory and ownership risks center on parser cleanup. `sqlite3ParserAddCleanup()` may run cleanup immediately on OOM; callers must not continue using freed pointers. `sqlite3Prepare()` may copy SQL text to ensure nul termination and then remap `sParse.zTail` back into the original buffer. UTF-16 tail mapping can be wrong if byte-length normalization or character counting changes.

## Test Signals
Preparation tests should cover legacy/v2/v3 APIs, persistent prep flags, tail pointers for nul-terminated and bounded SQL, SQL length limits, null API arguments under API armor, UTF-16 odd byte counts, UTF-16 tail mapping with multibyte characters, and saved-SQL automatic reprepare preserving bindings.

Schema tests should cover empty databases, attached database encoding mismatch, unsupported file format, reset-database mode, corrupt schema rows, non-`CREATE` schema SQL, orphan indexes, invalid and duplicate root pages, implicit unique/primary-key indexes with blank SQL, `SQLITE_WriteSchema`, `SQLITE_NoSchemaError`, and schema scans with authorizer callbacks disabled.

Concurrency tests should exercise shared-cache schema locks, schema cookie mismatch after another connection changes DDL, busy-handler reset after prepare, virtual-table disconnect unlocking before parse, and bounded retry behavior for `SQLITE_ERROR_RETRY` and `SQLITE_SCHEMA`.
