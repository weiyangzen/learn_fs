# sources/storage-engines/sqlite/src/attach.c

## Purpose

`attach.c` implements SQL `ATTACH` and `DETACH` plus the database-name fixing logic used when compiling persistent views, triggers, and indexes. It manages the `sqlite3.aDb[]` array, opens and closes attached btrees, validates schema compatibility, and prevents non-TEMP schema objects from referencing objects in a different attached database.

## Important APIs, Types, And Functions

Parser-facing entry points are `sqlite3Attach()` and `sqlite3Detach()`. They both call `codeAttach()`, which resolves expressions, runs authorization with `SQLITE_ATTACH` or `SQLITE_DETACH`, emits calls to internal SQL functions, and expires prepared statements. Runtime work happens in `attachFunc()` and `detachFunc()`, registered as `sqlite_attach` and `sqlite_detach` function definitions.

`sqlite3DbIsNamed()` compares a schema index with a requested name, treating database zero as both its stored schema name and `main`. The DDL fixer API is `sqlite3FixInit()`, `sqlite3FixSrcList()`, `sqlite3FixSelect()`, `sqlite3FixExpr()`, and `sqlite3FixTriggerStep()`. These use a `Walker` embedded in `DbFixer`, with `fixExprCb()` rejecting variables in normal DDL and `fixSelectCb()` pinning source items to the target schema.

## Control Flow

`resolveAttachExpr()` treats a top-level bare identifier in `ATTACH` or `DETACH` as a string literal, while still resolving more complex expressions normally. `codeAttach()` reads the schema, resolves file/name/key expressions, checks authorization using the original file/name expression when available, evaluates arguments into registers, invokes the internal function, and emits `OP_Expire`; ATTACH expires only the current statement, while DETACH expires all statements.

`attachFunc()` handles two paths. The special deserialize path, gated by `db->init.reopenMemdb`, replaces an existing database slot with a new `memdb` btree after verifying no transaction or backup is active. The normal path checks the attached database limit, rejects duplicate schema names, grows `db->aDb`, parses URI flags, applies `SQLITE_AttachWrite` and `SQLITE_AttachCreate` restrictions, opens a btree, installs a schema, applies pager settings, validates text encoding, initializes the attached schema, and rolls back all state on any error.

`detachFunc()` resolves the schema by name, rejects unknown, `main`, and `temp` detach attempts, rejects active transactions or backups, retargets TEMP triggers that referenced the detached schema, closes the btree, clears the schema pointer, and collapses the database array.

## State And Persistence Behavior

ATTACH modifies only connection-local state until the attached file is opened and its schema read. It updates `db->aDb`, `db->nDb`, `Db.pBt`, `Db.pSchema`, `Db.zDbSName`, safety level, pager locking mode, secure-delete behavior, synchronous flags, `db->noSharedCache`, `db->init.iDb`, and `DBFLAG_SchemaKnownOk`. The attached database file itself persists independently through the btree/pager layer. DETACH removes the connection's handle to that file but does not delete the file.

DDL fixing persists indirectly by rewriting parse-tree source items: it sets fixed schema metadata, records `fromDDL`, rewrites variables to NULL during initialization, and rejects cross-database references for non-TEMP objects before those definitions are stored in schema tables.

## Dependencies And Integration Points

This file integrates parser expressions, authorization, VDBE code generation, URI parsing, VFS lookup, btree open/close, pager pragmas, shared-cache mutex entry, schema initialization, trigger/view walkers, UPSERT trigger steps, and optional deserialize support. It is conditionally compiled by `SQLITE_OMIT_ATTACH`, with DDL-fixer pieces still present because schema object validation is needed outside normal ATTACH support.

## Risks And Edge Cases

Risk is concentrated in partial state transitions. `attachFunc()` increments `db->nDb` before all validation succeeds, so the cleanup path must close btrees, reset schemas, decrement `nDb`, and preserve useful error messages. Duplicate names, read-only attach flags, create suppression, URI parse errors, incompatible encodings, schema-init errors, active backups, and memory failures all have distinct behavior. DDL fixing must correctly allow TEMP objects to reference any schema while preventing persistent cross-schema dependencies. Bare identifiers are stringified only at the root of ATTACH/DETACH expressions, so concatenated identifiers still resolve normally and may fail.

## Test Signals

Signals include ATTACH/DETACH success across URI, readonly, create/no-create, and encrypted-key syntaxes; duplicate schema-name rejection; attached database limit enforcement; incompatible encoding errors; rollback after schema-init failure; DETACH rejection for main/temp, active transactions, and backup state; prepared-statement expiry semantics; TEMP trigger retargeting after detach; and DDL tests proving non-TEMP views, triggers, and indexes cannot reference objects in another database.
