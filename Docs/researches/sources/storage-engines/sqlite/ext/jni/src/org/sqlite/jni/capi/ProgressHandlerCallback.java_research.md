# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ProgressHandlerCallback.java

## Purpose
Callback interface for SQLite progress-handler interruption decisions.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call()`.

## Control Flow
SQLite invokes the callback every configured number of virtual machine opcodes. Return non-zero to interrupt the running operation.

## State And Persistence Behavior
No interface state. Installed callback is associated with a database handle and can consult external cancellation state.

## Dependencies And Integration Points
Installed with `CApi.sqlite3_progress_handler`.

## Risks And Edge Cases
Runs frequently on query execution hot paths, so it must be cheap. Exceptions are converted to database error information and suppressed.

## Test Signals
Long-running query interruption, clearing handler with null, invocation count behavior, and exception-to-error propagation.
