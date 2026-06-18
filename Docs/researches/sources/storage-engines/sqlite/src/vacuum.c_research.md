# sources/storage-engines/sqlite/src/vacuum.c

## Purpose
`vacuum.c` implements the SQL `VACUUM` command and the VDBE runtime operation that rebuilds a database into a compact copy, optionally writing to a separate output file for `VACUUM INTO`. It coordinates SQL schema replay, content copy, btree metadata preservation, pager flags, page-size/autovacuum settings, locking, and cleanup of the temporary attached vacuum database.

## Important APIs, Types, And Functions
The parser-facing entry point is `sqlite3Vacuum(Parse *pParse, Token *pNm, Expr *pInto)`, which emits `OP_Vacuum`. The runtime entry point is `sqlite3RunVacuum(char **pzErrMsg, sqlite3 *db, int iDb, sqlite3_value *pOut)`, called by the VDBE. Private helpers `execSql()` and `execSqlF()` prepare and run SQL against the same connection; when a SELECT returns SQL text, `execSql()` recursively executes only schema-copy statements beginning with `CRE` or `INS`.

Important data types are `sqlite3`, `Parse`, `Vdbe`, `Btree`, `Pager`, `Db`, `sqlite3_value`, `sqlite3_stmt`, and btree metadata constants such as `BTREE_SCHEMA_VERSION`, `BTREE_TEXT_ENCODING`, `BTREE_USER_VERSION`, and `BTREE_APPLICATION_ID`.

## Control Flow
`sqlite3Vacuum()` resolves an optional schema name, rejects the temp database, resolves an optional INTO expression into a register, emits `OP_Vacuum`, and marks the target btree as used. The heavy work occurs when VDBE executes the opcode and calls `sqlite3RunVacuum()`.

`sqlite3RunVacuum()` first rejects invocation inside a transaction or while other statements are active. For `VACUUM INTO`, it validates a text filename and temporarily forces create/readwrite open flags. It saves connection flags, change counters, trace state, and open flags; enables writable schema, built-in preference, attach create/write, comments, and vacuum mode; disables foreign keys, defensive mode, reverse order, and count-rows; and chooses a random attached schema name like `vacuum_...`.

It attaches the transient output database, verifies a `VACUUM INTO` target is empty, configures cache/spill/pager flags and reserved bytes, begins an SQL transaction, starts a btree transaction on the main database, sets target page size/autovacuum, replays table and index creation SQL from the source schema into the vacuum database, copies table contents with generated `INSERT INTO vacuum_db.table SELECT * FROM main.table` statements, copies view/trigger/virtual-table schema rows, preserves selected btree meta values while incrementing the schema cookie, copies the compacted file back with `sqlite3BtreeCopyFile()` for ordinary VACUUM, commits the temp btree, adjusts main page size/autovacuum metadata, then restores flags, closes/detaches the temporary btree, resets schemas, and returns the final rc.

## State And Persistence Behavior
Ordinary VACUUM rewrites the target database file through btree copy, requiring an exclusive transaction and enough temporary space for the vacuum copy and rollback journal. `VACUUM INTO` writes a separate output database and does not copy back into the source. The command preserves text encoding, user version, application id, cache-size metadata, and increments the schema version. It may apply pending `nextPagesize` and `nextAutovac` settings when allowed, but suppresses page-size changes for WAL-mode ordinary VACUUM.

Connection state is deliberately distorted during the operation and then restored: schema writes are allowed, checks and foreign keys are ignored while rebuilding, tracing is disabled, change counters are restored, and all schemas are reset at the end. The temporary attached database is closed manually after forcing `autoCommit=1` so its journal disappears with the pager close.

## Dependencies And Integration Points
`vacuum.c` depends on parser/VDBE code generation, `vdbe.c` `OP_Vacuum`, attach/database-name handling, SQL prepare/step/finalize APIs, btree and pager APIs, schema initialization, SQLite random number generation, URI parameter handling for reserve bytes, transaction state, and schema reset. It interacts with `sqlite_schema` content and therefore with `build.c`, `insert.c`, btree metadata, WAL journal mode, auto-vacuum settings, page-size pragmas, and VFS file behavior.

## Risks And Edge Cases
Security-sensitive behavior is concentrated in `execSql()`: schema SQL returned by SELECT is recursively executed only if it begins with `CREATE` or `INSERT`, limiting attacks that corrupt `sqlite_schema.sql` before VACUUM. Other risks include transaction-state enforcement, active statement detection, output-file existence checks for `VACUUM INTO`, WAL page-size restrictions, exact restoration of connection flags on error, random attached-schema naming collisions, reserved-byte URI handling, and correct manual detach cleanup. Failing after the temporary database is attached must still restore flags and reset schemas.

Because VACUUM rebuilds through SQL text from `sqlite_schema`, malformed or legacy schema entries can surface as prepare/runtime errors. The code assumes enough disk space for large temporary copies. `VACUUM INTO` must not overwrite an existing non-empty file. Btree metadata copy must increment the schema cookie so other connections reload the schema.

## Test Signals
Relevant tests include `vacuum*.test`, `interrupt.test` VACUUM cases, `enc2.test` encoding plus vacuum coverage, `autovacuum*.test`, `wal*.test` page-size/journal interactions, crash and corruption tests involving schema SQL, and `tt3_vacuum.c` concurrent writer/vacuum stress. Strong checks include "cannot VACUUM from within a transaction", "cannot VACUUM - SQL statements in progress", non-text INTO filename errors, output file already exists, page-size changes outside WAL, `PRAGMA integrity_check` after VACUUM, schema cookie changes, VACUUM INTO preserving source database, and cleanup after injected prepare/step/btree failures.
