# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.cpp

## Purpose
Implements RAII ownership and move semantics for `WT_SESSION *`, plus a helper to open `scoped_cursor` objects.

## Important APIs, Types, And Functions
Constructor calls `reinit`, destructor closes the session, move constructor and assignment swap ownership, `close_session` explicitly closes, `reinit` opens a session from a connection, pointer-like operators expose the session, and `open_scoped_cursor` returns a cursor wrapper.

## Control Flow
`reinit` closes any existing session, then calls `WT_CONNECTION::open_session` when a non-null connection is supplied. Move assignment mirrors the cursor wrapper: move-construct a temporary and swap so old state closes at scope exit.

## State And Persistence Behavior
Owns one session pointer. Session lifetime controls implicit cursor cleanup in WiredTiger and transaction context. `close_session` sets the wrapper to null after close.

## Dependencies And Integration Points
Depends on `test_util`, `scoped_cursor`, and WiredTiger APIs. Created by `connection_manager::create_session` and stored in `thread_worker`.

## Risks And Test Signals
Pointer-like operators assume a valid session. `close_session` does not guard against null before calling close, so callers should only use it on an initialized wrapper. Session close errors abort.
