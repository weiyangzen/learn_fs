# sources/storage-engines/sqlite/src/vtab.c research

## Purpose
`vtab.c` is the core virtual table integration layer. It registers modules, parses `CREATE VIRTUAL TABLE`, invokes constructors/destructors, implements declaration/configuration APIs, manages per-connection `VTable` objects, coordinates virtual table transactions/savepoints, supports function overloading, and creates/clears eponymous virtual tables.

## Important APIs, types, and functions
Important entry points include `sqlite3_create_module()`, `sqlite3_create_module_v2()`, `sqlite3_drop_modules()`, `sqlite3VtabBeginParse()`, `sqlite3VtabFinishParse()`, `sqlite3VtabCallConnect()`, `sqlite3VtabCallCreate()`, `sqlite3_declare_vtab()`, `sqlite3VtabCallDestroy()`, `sqlite3VtabBegin()`, `sqlite3VtabSync()`, `sqlite3VtabCommit()`, `sqlite3VtabRollback()`, `sqlite3VtabSavepoint()`, `sqlite3VtabOverloadFunction()`, `sqlite3VtabMakeWritable()`, `sqlite3VtabEponymousTableInit()`, `sqlite3_vtab_on_conflict()`, and `sqlite3_vtab_config()`.

## Control flow
Module registration installs a reference-counted `Module` in `db->aModule`. CREATE VIRTUAL TABLE parsing records module arguments, updates `sqlite_schema`, and emits `OP_VCreate` for real DDL. Constructors allocate `VTable`, install `db->pVtabCtx`, call `xCreate`/`xConnect`, require `sqlite3_declare_vtab()`, link the result, and strip `hidden` tokens from declared columns. Transaction flow adds vtabs to `db->aVTrans` on `xBegin`, calls `xSync`, then finalizes with `xCommit`/`xRollback`, including savepoint callbacks for version >= 2 modules.

## State and persistence behavior
Persistent schema rows are written for CREATE VIRTUAL TABLE, while module storage is owned by extension callbacks. Runtime state includes `db->aModule`, `Table.u.vtab` arguments and per-connection `VTable` lists, deferred disconnect list `pDisconnect`, active transaction array `aVTrans`, and eponymous module table caches.

## Dependencies and integration points
Depends on parser/schema/VDBE DDL machinery, authorization, mutex/shared-cache rules, `sqlite3_module`, table/index metadata, function resolution, savepoint constants, defensive flags, and API armor. Integrates with planning/name resolution, DML code generation, extension APIs, and virtual table xFindFunction overloads.

## Risks and test signals
Risks include constructor recursion, missing schema declaration, hidden-column mutation, shared-cache disconnect ordering, DROP with active references, misuse of `sqlite3_vtab_config()`, and transaction reference leaks. Test module replace/drop, constructor failures, hidden columns, WITHOUT ROWID constraints, schema reload, connect reuse, DROP locking, transaction/savepoint callback order, eponymous tables, overload functions, conflict mode, and API armor misuse.
