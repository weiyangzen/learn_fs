# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/tap2subunit.py

## Purpose

`tap2subunit.py` is the command wrapper that converts TAP text from stdin into subunit output.

## Important APIs, Types, and Functions

`main()` calls `TAP2SubUnit(sys.stdin, sys.stdout)`. The executable block exits with that return code.

## Control Flow

All TAP parsing and subunit generation happen in `subunit.TAP2SubUnit`. This wrapper only wires standard streams to the converter.

## State and Persistence Behavior

No wrapper state is persisted. The converter writes subunit v2 bytes to stdout.

## Dependencies and Integration Points

It depends on the public `TAP2SubUnit` helper. It integrates TAP-emitting test programs with subunit pipelines.

## Risks and Test Signals

The wrapper assumes stdout is suitable for byte output even though it passes `sys.stdout`. `test_tap2subunit.py` heavily validates the converter's behavior for TAP plans, skip/TODO directives, comments, bailouts, missing tests, trailing plans, and unnamed tests.
