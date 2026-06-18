# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.cpp

## Purpose
Implements RAII ownership and move semantics for `WT_CURSOR *`.

## Important APIs, Types, And Functions
Constructor opens a cursor through `reinit`. Move constructor and move assignment transfer cursor ownership by swapping. Destructor closes the cursor. Pointer-like access is exposed through `operator*`, `operator->`, and `get`.

## Control Flow
`reinit` asserts a non-empty URI, closes any currently owned cursor, and opens a new one when a non-null session is supplied. Move assignment constructs a temporary from the source and swaps internals so the old cursor closes when the temporary is destroyed.

## State And Persistence Behavior
Owns a single cursor pointer. The wrapper does not persist by itself but all cursor operations performed through it may read or mutate WiredTiger state. Destruction closes the cursor and can release pinned pages/resources.

## Dependencies And Integration Points
Depends on `test_util` and WiredTiger session/cursor APIs. Returned by `scoped_session::open_scoped_cursor` and stored widely in workers and tests.

## Risks And Test Signals
`operator->` and `operator*` assume `_cursor` is non-null; callers must check `get()` when using default-constructed or moved-from objects. Closing errors abort through `testutil_check`.
