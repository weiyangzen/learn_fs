# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/run.py

## Purpose

`run.py` implements `python -m subunit.run`, a `unittest`/`testtools` runner that reports test enumeration and execution as subunit v2.

## Important APIs, Types, and Functions

`SubunitTestRunner` accepts runner options and writes to `stream` or `stdout`. `run(test)` lists tests, emits `exists` statuses, wraps the stream result with `ExtendedToStreamDecorator` and `AutoTimingTestResultDecorator`, then runs the test. `list(test, loader=None)` emits test ids and import errors. `_list(test)` uses `testtools.run.list_test` and `StreamResultToBytes`. `SubunitTestProgram` customizes usage text. `main(argv=None, stdout=None)` wires `TestProgram` to `SubunitTestRunner`.

## Control Flow

`main` optionally reopens stdout unbuffered for CLI use, then constructs a `TestProgram` with `exit=False` so normal test failures do not raise `SystemExit`. The runner enumerates test ids before execution, giving downstream consumers an `exists` inventory, then runs the suite with timing decoration. Loader/listing errors are emitted as unrunnable file status packets and exit 2.

## State and Persistence Behavior

State is held in the stream result and runner options. The module writes binary subunit packets to stdout/stream and persists no files.

## Dependencies and Integration Points

It depends on `testtools.run`, `testtools.ExtendedToStreamDecorator`, `subunit.StreamResultToBytes`, and `AutoTimingTestResultDecorator`. It is the main Python test execution integration point for subunit.

## Risks and Test Signals

Stream handling is subtle: `_list` reopens file descriptors in binary unbuffered mode when possible, and `main` rewrites `sys.stdout`. `test_run.py` verifies timing output, pre-run `exists` statuses, loader errors, non-exit behavior for failing tests, and `SystemExit` behavior for execution errors.
