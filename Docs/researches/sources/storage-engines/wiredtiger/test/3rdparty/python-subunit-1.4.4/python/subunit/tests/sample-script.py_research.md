# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-script.py

## Purpose

`sample-script.py` is a tiny executable fixture used by protocol/exec tests to emit deterministic subunit v1-style output.

## Important APIs, Types, and Functions

The script imports `sys` and writes fixed lines to `sys.stdout`: one successful test, one failing test with bracketed details, and one error test with bracketed details.

## Control Flow

Execution is linear. It emits `test`, `success`, `failure [`, detail lines, `]`, then another `test` and `error [` block. There are no functions or CLI arguments.

## State and Persistence Behavior

The script writes only stdout and maintains no state.

## Dependencies and Integration Points

It integrates with `ExecTestCase` and parser tests that need an external command producing subunit. Because it writes strings, callers must account for text-to-byte conversion depending on Python runtime.

## Risks and Test Signals

The fixture is intentionally static. The main risk is execution permissions or stdout text mode in tests expecting bytes. Validation is that parser tests consume its output and produce the expected success, failure, and error events.
