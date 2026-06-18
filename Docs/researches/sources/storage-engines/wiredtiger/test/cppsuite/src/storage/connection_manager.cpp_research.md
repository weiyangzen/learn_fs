# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.cpp

## Purpose
Implements a singleton owner for the active WiredTiger connection and factory for RAII sessions.

## Important APIs, Types, And Functions
`connection_manager::instance`, destructor, `close`, `create`, `reopen`, `create_session`, `get_connection`, `set_timestamp`, and private constructor are implemented here.

## Control Flow
`create` rejects reopening when `_conn` is non-null, logs the open config, asserts the home path does not already exist, creates the home directory, optionally creates a journal directory and nested subdirectories, then calls `wiredtiger_open`. `reopen` opens an existing home without creating it. `create_session` validates `_conn`, locks `_conn_mutex`, constructs a `scoped_session`, and returns it by move. `set_timestamp` serializes calls with the same mutex.

## State And Persistence Behavior
Owns the process-wide `WT_CONNECTION *`. `create` creates filesystem directories for WiredTiger homes and opens persistent database state. `close` closes the connection and nulls the pointer. The singleton destructor closes any remaining connection.

## Dependencies And Integration Points
Depends on `logger`, `test_util`, `scoped_session`, WiredTiger C API, and `SUB_DIR` constants. Used by `test::run`, population, validation, and custom tests needing sessions or direct connection APIs.

## Risks And Test Signals
Only session creation and timestamp setting are mutex-protected; callers using `get_connection` directly must handle their own synchronization where necessary. `create` asserts the home path is absent, while `test::run` removes it first. A failed close/open aborts through test utility checks.
