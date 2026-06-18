# sources/storage-engines/sqlite/src/auth.c

## Purpose

`auth.c` implements the optional `sqlite3_set_authorizer()` facility. It stores a user callback on the database handle and invokes it during SQL compilation to approve, deny, or ignore operations such as reading columns, updating tables, creating objects, running pragmas, transactions, ATTACH, and DETACH.

## Important APIs, Types, And Functions

The public API is `sqlite3_set_authorizer(sqlite3*, xAuth, void*)`, which installs or clears `db->xAuth` and `db->pAuthArg` under the connection mutex and expires existing prepared statements. `sqlite3AuthCheck()` is the common fast path used by parser/compiler code. It returns `SQLITE_OK` when no callback is installed or initialization is active, otherwise delegates to `realAuthCheck()`.

Column-read authorization is split into `sqlite3AuthRead()` and `sqlite3AuthReadCol()`. `sqlite3AuthRead()` maps a `TK_COLUMN` or trigger pseudo-column expression to a table, column name, schema index, and rowid/primary-key spelling. `sqlite3AuthReadCol()` invokes the callback with `SQLITE_READ` and writes detailed errors for denial. Authorization context is managed with `sqlite3AuthContextPush()` and `sqlite3AuthContextPop()`, which temporarily set `Parse.zAuthContext`.

## Control Flow

Installing a callback is straightforward: optional API armor checks the database handle, the database mutex is entered, callback fields are assigned, prepared statements are expired, and the mutex is released. During compilation, callers first hit `sqlite3AuthCheck()`. If authorization is disabled or `db->init.busy` is true, it returns success without invoking user code. Otherwise `realAuthCheck()` skips special parser modes, calls `db->xAuth(pAuthArg, code, zArg1, zArg2, zArg3, zAuthContext)`, converts `SQLITE_DENY` into a parse error and `SQLITE_AUTH`, preserves `SQLITE_IGNORE`, and treats invalid return codes as an authorizer malfunction.

For column reads, denial records "access to ..." with table/column and optional database prefix. `SQLITE_IGNORE` changes a resolvable expression from `TK_COLUMN` to `TK_NULL`; if `sqlite3AuthReadCol()` is used without an expression to rewrite, callers must treat ignore as denial.

## State And Persistence Behavior

This file does not persist database content. Its state is connection-local: `sqlite3.xAuth`, `sqlite3.pAuthArg`, `Parse.zAuthContext`, `Parse.rc`, and parse error text. Installing or clearing the callback invalidates prepared statements so future compilation observes the new policy. Authorization is intentionally a compile-time gate; it does not recheck each row at execution time except through decisions baked into the compiled expression tree.

## Dependencies And Integration Points

The implementation depends on parser state, expression and source-list metadata, schemas, trigger compilation, connection mutexes, prepared-statement expiration, error formatting, and the constants published by the SQLite C API. It is entirely omitted under `SQLITE_OMIT_AUTHORIZATION` and contains API armor under `SQLITE_ENABLE_API_ARMOR`.

## Risks And Edge Cases

The main semantic risk is confusing compile-time authorization with runtime access control. Existing prepared statements are expired after policy changes, but applications that cache statements must handle reprepare. `SQLITE_IGNORE` has special read-column behavior: a denied read can silently become NULL rather than failing the statement. Initialization and special parse modes intentionally bypass callbacks to avoid blocking schema loading, virtual table declaration, and rename internals. Invalid callback return values deliberately become errors to surface buggy authorizers.

## Test Signals

Useful tests set callbacks that return each allowed and invalid result for `SQLITE_READ`, DDL, DML, PRAGMA, ATTACH, and transaction actions. Column tests should verify NULL substitution for ignored reads, error text for denied reads, trigger/view auth contexts, rowid and INTEGER PRIMARY KEY naming, statement expiration after changing the callback, and no callback during schema initialization or special parser modes.
