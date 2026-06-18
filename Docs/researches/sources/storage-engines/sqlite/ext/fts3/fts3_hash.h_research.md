# sources/storage-engines/sqlite/ext/fts3/fts3_hash.h

## Purpose

Declares the FTS3 standalone hash-table API and the concrete `Fts3Hash` and `Fts3HashElem` layouts. The file is intentionally not fully opaque because iteration and accessor operations are implemented as macros.

## Important APIs, types, and functions

`Fts3Hash` stores key mode, key-copy policy, element count, the first element in a global list, bucket count, and bucket array. `Fts3HashElem` stores global-list links, user data, key pointer, and key length. Key classes are `FTS3_HASH_STRING` and `FTS3_HASH_BINARY`. Declared operations are `sqlite3Fts3HashInit()`, `sqlite3Fts3HashInsert()`, `sqlite3Fts3HashFind()`, `sqlite3Fts3HashClear()`, and `sqlite3Fts3HashFindElem()`, with shorthand aliases and iteration macros.

## Control flow

Clients initialize a stack or embedded `Fts3Hash`, insert keyed data, find by key, optionally iterate using `fts3HashFirst()` and `fts3HashNext()`, and clear when done. Deletion is expressed by inserting `NULL` data for a key.

## State and persistence

The header defines in-memory state only. Ownership of keys is controlled by `copyKey`; ownership of `data` always remains with the caller unless a higher-level subsystem adds its own policy.

## Dependencies and integration points

The implementation lives in `fts3_hash.c`. `fts3_tokenizer.c`, `fts3_tokenize_vtab.c`, expression test setup, and FTS module initialization use this API to publish and resolve tokenizer implementations.

## Risks and test signals

Because structure fields are visible, misuse can corrupt internal invariants. Macro iteration assumes the table is not mutated unsafely while walking it. Tests that register tokenizers, query unknown tokenizers, clear module state, and run under OOM are the practical signals for this header/API contract.
