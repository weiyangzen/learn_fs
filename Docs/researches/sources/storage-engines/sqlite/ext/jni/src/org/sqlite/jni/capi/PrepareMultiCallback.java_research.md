# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PrepareMultiCallback.java

## Purpose
Callback interface used by `CApi.sqlite3_prepare_multi` to process each prepared statement from a multi-statement SQL input.

## Important APIs, Types, And Functions
Declares `int call(sqlite3_stmt st)`. Nested `Finalize` wraps another callback and always finalizes each statement. Nested `StepAll` steps through a statement until completion and returns zero for `SQLITE_DONE`.

## Control Flow
`sqlite3_prepare_multi` prepares statements one by one and transfers each non-empty statement to `call()`. The callback decides whether to finalize, retain, step, or stop. Non-zero returns stop the loop.

## State And Persistence Behavior
The interface has no state. Ownership of each `sqlite3_stmt` transfers to the callback. `Finalize` enforces cleanup in a `finally` block.

## Dependencies And Integration Points
Depends on `CallbackProxy`, `sqlite3_stmt`, and `CApi.sqlite3_step/finalize` constants. Used by Java multi-statement execution helpers and tests.

## Risks And Edge Cases
If a callback neither finalizes nor stores a statement for later finalization, native statements leak. Exceptions are converted by `sqlite3_prepare_multi` into database errors. `StepAll` itself does not finalize unless wrapped with `Finalize`.

## Test Signals
Multi-statement inputs with whitespace/comments, callback stop codes, exception conversion, finalization verification, and stepping result handling.
