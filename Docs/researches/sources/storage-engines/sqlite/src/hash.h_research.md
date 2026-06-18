# sources/storage-engines/sqlite/src/hash.h

## Purpose

`hash.h` declares SQLite's generic internal hash-table structure and access macros. It exposes enough layout for efficient iteration and count checks while documenting that callers should modify tables only through the functions implemented in `hash.c`.

## Important APIs, Types, And Functions

The header defines `Hash` and `HashElem`. `Hash` contains bucket count, entry count, the first element of the global list, and an optional bucket array whose entries store a count plus a pointer to the first element for that hash. `HashElem` contains next/previous list links, payload pointer, caller-owned key pointer, and cached hash value.

Declared functions are `sqlite3HashInit(Hash*)`, `sqlite3HashInsert(Hash*, const char *pKey, void *pData)`, `sqlite3HashFind(const Hash*, const char *pKey)`, and `sqlite3HashClear(Hash*)`. Macros are `sqliteHashFirst(H)`, `sqliteHashNext(E)`, `sqliteHashData(E)`, and `sqliteHashCount(H)`.

## Control Flow

The header itself has no runtime control flow. It establishes the iteration idiom: start at `sqliteHashFirst(&h)`, advance with `sqliteHashNext(p)`, and fetch payloads with `sqliteHashData(p)`. Deletion is expressed through `sqlite3HashInsert()` with a NULL payload.

## State And Persistence Behavior

`Hash` instances are embedded in higher-level in-memory objects such as schemas or function registries. The table owns its `HashElem` nodes and bucket array but not payloads or key strings. Nothing in the header represents persistent database state.

## Dependencies And Integration Points

`hash.h` is included by SQLite internals via `sqliteInt.h` and is coupled to `hash.c`'s bucket/list invariants. Schema code and function lookup code access `Hash` through this API and sometimes rely on the exposed macros for iteration and counts.

## Risks

Because the structures are visible, accidental direct mutation can corrupt bucket/list invariants. Iterating while inserting or deleting requires caller discipline. The key pointer is not copied, so transient key storage is unsafe. The commented-out key/keysize macros indicate the current implementation does not expose key data to callers through the public macro set.

## Test Signals

Signals are mostly the `hash.c` behavior tests plus compile coverage for users that embed `Hash`, iteration over schema hash tables, count accuracy through `sqliteHashCount()`, and ABI-sensitive builds that include this header through amalgamation and non-amalgamation paths.
