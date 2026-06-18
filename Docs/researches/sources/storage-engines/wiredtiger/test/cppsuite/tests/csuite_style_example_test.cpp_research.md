# sources/storage-engines/wiredtiger/test/cppsuite/tests/csuite_style_example_test.cpp

## Purpose
Provides a standalone example of writing a C++ test using cppsuite utilities without the full `test` framework lifecycle.

## Important APIs, Types, And Functions
Global flags `do_inserts` and `do_reads` drive thread loops. Static `insert_op` and `read_op` use raw `WT_CURSOR *`. `main` demonstrates logging, connection creation, session/cursor management, simple CRUD checks, thread manager use, and cleanup.

## Control Flow
`main` sets program name and log level, removes the test home, creates a connection, opens insert/read sessions and cursors, creates a table, inserts and searches sample keys, starts insert and read threads for five seconds, stops them by flipping globals, joins, closes cursors, and exits.

## State And Persistence Behavior
Creates a WiredTiger home and table, inserts random data concurrently, and searches random keys. It uses raw WiredTiger resources rather than RAII wrappers for sessions/cursors, except for the singleton connection manager.

## Dependencies And Integration Points
Depends on constants/logger/random generator/thread manager/connection manager and WiredTiger/test utility C headers. It is more of a template/demo than a framework-managed workload.

## Risks And Test Signals
Global bool flags are unsynchronized and suitable only for a simple example. Insert and read loops share raw cursors with their owning sessions and depend on the main thread closing after join. Duplicate random keys may cause insert errors depending on table overwrite behavior. Test signals are the initial expected search results and lack of runtime API failures.
