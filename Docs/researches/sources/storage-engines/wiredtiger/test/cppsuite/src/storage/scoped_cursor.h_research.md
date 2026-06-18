# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.h

## Purpose
Declares the move-only RAII cursor wrapper used throughout cppsuite.

## Important APIs, Types, And Functions
`scoped_cursor` supports default construction, construction from `WT_SESSION *`, URI, and config, move construction, move assignment, `reinit`, pointer-like operators, and `get`. Copy construction and copy assignment are deleted.

## Control Flow
The interface lets tests treat the wrapper like a `WT_CURSOR *` while preserving single ownership and automatic close behavior.

## State And Persistence Behavior
Private state is `_cursor`. Persistence effects depend on the cursor methods invoked by callers.

## Dependencies And Integration Points
Includes `wiredtiger.h`. It is the common cursor type in `thread_worker`, storage wrappers, validators, and test overrides.

## Risks And Test Signals
Moved-from cursors become null and must not be dereferenced. Default construction is useful for optional cursors such as worker stats cursors but requires later initialization.
