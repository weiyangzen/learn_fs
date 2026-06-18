# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.h

## Purpose
Declares the connection singleton used by the framework to manage one WiredTiger connection and create sessions.

## Important APIs, Types, And Functions
Public singleton API includes `instance`, deleted copy/assignment, destructor, `close`, `create`, `reopen`, `create_session`, `get_connection`, and `set_timestamp`. Private state is `_conn` and `_conn_mutex`.

## Control Flow
The header defines controlled construction through `instance()` and prevents copies. Callers open a connection with `create` or `reopen`, then request sessions or direct connection access.

## State And Persistence Behavior
The manager owns the active `WT_CONNECTION *` and mediates access to session creation and global timestamp mutation. Persistent data lives under the configured WiredTiger home.

## Dependencies And Integration Points
Includes `scoped_session.h` and mutex support. This type is referenced by the base harness and tests that need direct `WT_CONNECTION` APIs such as compiled configurations or cache reconfiguration.

## Risks And Test Signals
Direct `get_connection` access bypasses the mutex and returns a raw pointer. Because it is a singleton, tests in the same process must close or isolate connections carefully to avoid "connection is not NULL" failures.
