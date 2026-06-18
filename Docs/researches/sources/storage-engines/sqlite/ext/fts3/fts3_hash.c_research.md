# sources/storage-engines/sqlite/ext/fts3/fts3_hash.c

## Purpose

Provides the standalone hash-table implementation used by FTS3, mainly for tokenizer module registration and lookup. It is derived from SQLite's generic hash table but scoped to FTS and supports string or binary keys.

## Important APIs, types, and functions

Public functions are `sqlite3Fts3HashInit()`, `sqlite3Fts3HashClear()`, `sqlite3Fts3HashFindElem()`, `sqlite3Fts3HashFind()`, and `sqlite3Fts3HashInsert()`. Internal helpers include `fts3StrHash()`, `fts3BinHash()`, key comparators, `ftsHashFunction()`, `ftsCompareFunction()`, `fts3Rehash()`, `fts3HashInsertElement()`, `fts3FindElementByHash()`, and `fts3RemoveElementByHash()`.

## Control flow

Initialization records key class and ownership policy. Lookup computes a raw hash and masks it by the power-of-two bucket count. Insert first searches for an existing element; if found it updates data or removes the element when `data==NULL`. New inserts lazily allocate eight buckets and double the table when the element count reaches the bucket count. Rehash rebuilds bucket chains while preserving the global doubly linked element list.

## State and persistence

The table owns bucket arrays, element nodes, and optionally key copies. It stores only in-memory process state and persists nothing to SQLite tables. `sqlite3Fts3HashClear()` returns the table to an empty state and frees copied keys.

## Dependencies and integration points

Depends on SQLite memory routines through `fts3Int.h` and the declarations in `fts3_hash.h`. The tokenizer subsystem initializes a string/copy-key hash and stores `sqlite3_tokenizer_module *` values keyed by tokenizer names. Test and virtual-table code also uses the hash to resolve tokenizer names.

## Risks and test signals

OOM semantics are subtle: insert returns the input `data` if allocation fails, which callers must treat as failure. String keys use byte-counted `strncmp()` with case-sensitive matching, so callers must pass consistent `nKey` values including the nul byte for tokenizer names. Removal must keep both bucket chains and the global list valid. Test signals come from tokenizer registration/query tests, repeated insert/delete/clear cycles, OOM paths, and hash iteration macros.
