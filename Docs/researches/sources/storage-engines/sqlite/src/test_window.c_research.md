# sources/storage-engines/sqlite/src/test_window.c

## Purpose

`test_window.c` is SQLite testfixture support for registering window functions from Tcl. Under `SQLITE_TEST`, it exposes commands that call `sqlite3_create_window_function()`, verify misuse cases, register a strict integer-summing window aggregate, and override the built-in `sum` aggregate for tests.

## Important APIs, Types, And Functions

- `TestWindow` stores Tcl scripts for xStep, xFinal, xValue, xInverse, plus the interpreter.
- `TestWindowCtx` stores the current Tcl object aggregate value.
- `doTestWindowStep()` invokes either the Tcl xStep or xInverse script with the previous state and SQL arguments.
- `doTestWindowFinalize()` invokes Tcl xFinal or xValue and returns text to SQLite.
- `testWindowStep()`, `testWindowInverse()`, `testWindowFinal()`, `testWindowValue()`, and `testWindowDestroy()` are callbacks passed to SQLite.
- `test_create_window()` implements Tcl `sqlite3_create_window_function`.
- `test_create_window_misuse()` verifies that missing required callbacks return `SQLITE_MISUSE`.
- `sumintStep()`, `sumintInverse()`, `sumintFinal()`, and `sumintValue()` implement a one-argument integer-only window sum.
- `test_create_sumint()` and `test_override_sum()` register test functions.
- `Sqlitetest_window_Init()` installs the Tcl commands.

## Control Flow

The generic Tcl-backed window function is created by `sqlite3_create_window_function DB NAME XSTEP XFINAL XVALUE XINVERSE`. The command duplicates and reference-counts the four Tcl callback scripts, stores them in a `TestWindow`, and passes that object as `sqlite3_user_data()`.

For each step or inverse call, `doTestWindowStep()` duplicates the configured Tcl script, appends the previous aggregate value (or an empty string), appends string versions of all SQL arguments, and evaluates it globally. On Tcl success, the result replaces `TestWindowCtx.pVal`; on error, SQLite receives `sqlite3_result_error()`. For xValue/xFinal, `doTestWindowFinalize()` evaluates the selected Tcl script with the current state and returns its string result. xFinal also releases the stored state.

The `sumint` implementation uses SQLite aggregate context as a `sqlite3_int64`, adds integer arguments in xStep, subtracts in xInverse, and returns the current sum in both xValue and xFinal. Non-integer xStep arguments produce an error.

## State And Persistence Behavior

All state is per connection and per aggregate/window frame. The registered function's `TestWindow` persists until SQLite destroys the function object and invokes `testWindowDestroy()`. Aggregate state persists in `sqlite3_aggregate_context()` for each invocation context and owns a Tcl object reference when the Tcl-backed function is used. The file does not persist database content except through SQL statements that call the registered functions.

## Dependencies And Integration Points

The file depends on `sqlite3_create_window_function()`, `sqlite3_create_function()`, SQLite aggregate context APIs, Tcl object evaluation, testfixture `getDbPointer()`, and `sqlite3ErrName()`. It integrates with window-function planner and executor tests, function registration API tests, and misuse validation.

## Risks And Edge Cases

- `sqlite3_value_text()` is used for all generic Tcl callback arguments, so NULL and non-text values are coerced to text-oriented representations for tests.
- xInverse assumes the aggregate context exists in `sumintInverse()` and does not validate integer type; this is acceptable for controlled tests but not a general extension pattern.
- The generic Tcl-backed function returns all values as text, which may affect affinity-sensitive tests.
- Callback scripts are evaluated globally in the stored interpreter, so tests must manage global Tcl state and errors carefully.
- On `sqlite3_create_window_function()` failure, `test_create_window()` returns an error without explicitly freeing `pNew`; expected SQLite destructor behavior should be checked for registration failures.

## Test Signals

Tests should cover custom Tcl step/inverse/value/final call ordering, state propagation between callbacks, error propagation from Tcl scripts, xFinal state cleanup, `SQLITE_MISUSE` for missing callback combinations, `sumint` over sliding windows, non-integer argument errors, and overriding `sum` through normal aggregate registration.
