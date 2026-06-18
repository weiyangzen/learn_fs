# sources/storage-engines/sqlite/ext/misc/anycollseq.c

## Purpose
`anycollseq.c` is a small loadable extension that installs a `sqlite3_collation_needed()` callback. Whenever SQLite encounters an unknown collation sequence, the extension registers a fallback collation that compares bytes like `BINARY`.

## Important APIs, types, and functions
- `anyCollFunc()` compares two byte strings with `memcmp()` and length fallback.
- `anyCollNeeded()` registers `anyCollFunc()` for the requested collation name and text encoding.
- `sqlite3_anycollseq_init()` initializes extension API pointers and installs the collation-needed callback.

## Control flow
Loading the extension calls `sqlite3_collation_needed()`. Later, schema parsing or SQL execution that references an unknown collation triggers `anyCollNeeded()`, which calls `sqlite3_create_collation()` with the missing name and a binary-compatible comparator.

## State and persistence behavior
No persistent state is created. Registered collations live on the database connection after callback invocation. The extension uses no heap allocation.

## Dependencies and integration points
It depends on `sqlite3ext.h`, SQLite extension loading, collation-needed callbacks, and `string.h`. It is useful when loading schemas that mention collations absent from the current process.

## Risks and edge cases
The fallback collation may make schema loading possible but can change query ordering or uniqueness semantics if the original collation was not binary-equivalent. It intentionally ignores `pzErrMsg` and callback user data.

## Test signals
Load the extension, open or create a schema using an unknown collation, then query/order data under that collation. Expected behavior is no missing-collation error and bytewise ordering.
