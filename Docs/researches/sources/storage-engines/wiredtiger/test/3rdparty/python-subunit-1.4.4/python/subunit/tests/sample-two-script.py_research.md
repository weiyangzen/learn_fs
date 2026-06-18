# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-two-script.py

## Purpose

`sample-two-script.py` is a second minimal external fixture for tests that need a separate subunit-emitting script.

## Important APIs, Types, and Functions

The script imports `sys` and writes a single successful subunit v1 test named `sample two`.

## Control Flow

Execution writes `test sample two` followed by `success sample two` to stdout. There are no functions or arguments.

## State and Persistence Behavior

No state is retained and no files are written.

## Dependencies and Integration Points

It is an integration fixture for external script execution paths, especially `ExecTestCase`-style tests.

## Risks and Test Signals

Risk is limited to executable discovery and stdout encoding. A passing integration test should observe exactly one successful remoted test from this script.
