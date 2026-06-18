# sources/storage-engines/sqlite/src/test_wsd.c

## Purpose

`test_wsd.c` provides sample test implementations of `sqlite3_wsd_init()` and `sqlite3_wsd_find()` for builds that define both `SQLITE_OMIT_WSD` and `SQLITE_TEST`. WSD means writable static data; this shim emulates SQLite's writable static variables using process-local heap storage.

## Important APIs, Types, And Functions

- `ProcessLocalStorage` contains a fixed hash table of `ProcessLocalVar` entries and a bump-allocation free area.
- `ProcessLocalVar` stores the original static variable key pointer and hash-chain link; the variable bytes follow the structure in memory.
- `pGlobal` is the single process-local storage arena.
- `sqlite3_wsd_init(int N, int J)` allocates the arena sized for `N` bytes of variable data plus `J` hash entries.
- `sqlite3_wsd_find(void *K, int L)` hashes the key pointer, returns an existing copy, or creates a new entry initialized from the bytes at `K`.

## Control Flow

`sqlite3_wsd_init()` lazily allocates one contiguous block with `malloc()`, clears the `ProcessLocalStorage` header, and points `pFree` after it. `sqlite3_wsd_find()` hashes the address value of `K`, searches the bucket chain for pointer identity, and if absent consumes `ROUND8(sizeof(ProcessLocalVar)+L)` bytes from the arena, links a new entry, copies `L` bytes from `K`, and returns the storage after the entry header.

## State And Persistence Behavior

The arena is process-global and never freed by this file. It persists for the life of the test process. Each emulated WSD variable is initialized once from the original static memory image and then remains mutable in the process-local copy. There is no thread synchronization in this sample implementation.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, `ROUND8`, SQLite result constants, and C heap functions. It is only compiled in a specialized test build and supplies symbols expected by SQLite's `SQLITE_OMIT_WSD` mode.

## Risks And Edge Cases

- The implementation asserts enough arena space exists rather than returning an error from `sqlite3_wsd_find()`, so incorrect `N`/`J` sizing is fatal in debug builds and unsafe otherwise.
- `pGlobal` access is unsynchronized; concurrent first access or variable creation can race.
- Hashing pointer bytes is process-specific and uses only pointer identity, which is appropriate for static-variable keys but not generalized keys.
- There is no cleanup path and no support for per-thread storage isolation.

## Test Signals

Tests should use an `SQLITE_OMIT_WSD && SQLITE_TEST` build, call SQLite initialization paths that invoke `sqlite3_wsd_init()`, verify repeated `sqlite3_wsd_find()` calls for the same key return the same mutable copy, verify different keys do not alias, and stress arena sizing for all expected WSD variables.
