# sources/storage-engines/sqlite/src/callback.c

## Purpose

`callback.c` maintains SQLite connection-local registries for collating sequences and application-defined SQL functions, plus schema-object cleanup and schema allocation. It is not a user callback dispatcher in the general sense; instead it supports callbacks that provide missing collations (`xCollNeeded`/`xCollNeeded16`) and manages the hash-table entries that later parser, expression, and VDBE code use when resolving SQL names.

## Important APIs, Types, and Functions

- `sqlite3FindCollSeq()` locates or optionally creates one of the three `CollSeq` entries associated with a collation name. Each hash entry stores UTF-8, UTF-16LE, and UTF-16BE variants plus a single trailing name string.
- `sqlite3GetCollSeq()` is the resolving wrapper that invokes the collation-needed callback and can synthesize a collation from another encoding using `synthCollSeq()`.
- `sqlite3LocateCollSeq()` resolves by database-native encoding during parsing and creates placeholder entries while schema initialization is busy.
- `sqlite3SetTextEncoding()` changes `db->enc`, resets `db->pDfltColl` to `BINARY`, and expires prepared statements.
- `matchQuality()` scores candidate `FuncDef` entries by argument count and text encoding. `sqlite3FindFunction()` uses it to search application functions first, then built-ins unless creation is requested.
- `sqlite3InsertBuiltinFuncs()` inserts compile-time function definitions into the global `sqlite3BuiltinFunctions` hash, chaining overloads with the same name.
- `sqlite3SchemaClear()` tears down `Schema` hash contents for tables, triggers, indexes, and foreign keys. `sqlite3SchemaGet()` obtains or initializes the schema object attached to a `Btree` or allocates a standalone schema.

Core data structures are `CollSeq`, `FuncDef`, `Schema`, `Hash`, `HashElem`, `Table`, `Trigger`, and `Btree`, all defined in SQLite internals.

## Control Flow and Behavior

Collation lookup begins with `findCollSeqEntry()`, which returns a three-entry encoding array or creates one when allowed. If a collation exists but has no comparison function, `sqlite3GetCollSeq()` calls `callCollNeeded()`. The UTF-8 callback gets a database-owned copy of the name; the UTF-16 callback builds a transient `sqlite3_value` to convert the name to native UTF-16. If the exact encoding remains unresolved, `synthCollSeq()` searches alternate encodings and copies the usable `CollSeq` while intentionally dropping the copied destructor pointer.

Function lookup uses a two-level search. Application-defined functions live in `db->aFunc` and are linked through `pNext`; built-ins live in `sqlite3BuiltinFunctions.a[h]` and can also have `pNext` overload chains. `sqlite3FindFunction()` chooses the highest `matchQuality()` score. With `createFlag`, it allocates a new lowercase-name `FuncDef`, inserts it into the per-connection hash, and returns only mutable application-owned entries.

Schema cleanup snapshots the table and trigger hashes, reinitializes schema hash heads first, and then deletes objects using a zeroed fake `sqlite3` handle. This avoids recursive stale hash traversal while freeing nested table and trigger resources.

## State and Persistence

The file mutates connection-local state: `db->aCollSeq`, `db->aFunc`, `db->enc`, `db->pDfltColl`, `db->mDbFlags`, and schema hash members. Built-in function registration mutates global `sqlite3BuiltinFunctions`. Schema clearing increments `Schema.iGeneration` when a loaded schema is reset and clears `DB_SchemaLoaded`/`DB_ResetWanted`, which invalidates dependent prepared statements elsewhere. No database pages are written directly here.

## Dependencies and Integration Points

This code depends on SQLite hash APIs, allocator APIs, string comparison helpers, parser error reporting, value conversion, trigger/table deletion, and B-tree schema storage. It is called from parser name resolution, function registration APIs, collation registration APIs, schema reset paths, and date/time or other built-in function registration (`sqlite3InsertBuiltinFuncs()` is used by multiple modules).

## Risks and Edge Cases

Collation fallback intentionally copies function pointers but not destructors; copying `xDel` would double-free external collation state. OOM paths must signal `sqlite3OomFault()` and leave hash tables consistent. `sqlite3FindFunction()` must not return built-in definitions while creating a new function because callers overwrite returned fields. `matchQuality()` has special negative arity rules for built-ins with one-or-more or two-or-more arguments. Schema cleanup order is sensitive because table deletion can refer to trigger/index/fkey structures.

## Test Signals

Useful tests include collation-needed callbacks for UTF-8 and UTF-16 names, missing collation error text and `SQLITE_ERROR_MISSING_COLLSEQ`, fallback across encoding-specific collations, application functions overriding built-ins and `DBFLAG_PreferBuiltin`, vararg and fixed-arity function resolution, OOM during hash insertion, schema reset generation increments, and deletion of schemas containing tables, indexes, triggers, and foreign keys.
