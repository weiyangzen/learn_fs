# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.h

## Purpose
Declares the move-only RAII session wrapper used for WiredTiger session lifetime management.

## Important APIs, Types, And Functions
`scoped_session` supports default construction, construction from `WT_CONNECTION *`, move construction, move assignment, `reinit`, pointer-like operators, `get`, `open_scoped_cursor`, and `close_session`. Copy operations are deleted.

## Control Flow
The interface encourages session ownership transfer into workers and local validation scopes while keeping cursor opening concise.

## State And Persistence Behavior
Private state is `_session`. Persistent effects are through transaction, cursor, checkpoint, compact, and truncate calls made by users of the session.

## Dependencies And Integration Points
Includes `scoped_cursor.h` and `wiredtiger.h`. It is returned by `connection_manager` and used in nearly all cppsuite database interactions.

## Risks And Test Signals
Moved-from or default sessions have null `_session`; dereferencing them is invalid. Cursor wrappers created from a session should not outlive the session.
