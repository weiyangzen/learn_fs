# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_output.py

## Purpose

`subunit_output.py` is the console/module wrapper for `_output.output_main`.

## Important APIs, Types, and Functions

`main()` returns `output_main()`. The executable block exits with that return code.

## Control Flow

All argument parsing and stream generation are delegated to `subunit._output`.

## State and Persistence Behavior

This wrapper creates no state. `_output` writes the generated v2 stream to stdout.

## Dependencies and Integration Points

It integrates packaging entry points and `python -m subunit.filter_scripts.subunit_output` with the implementation in `_output.py`.

## Risks and Test Signals

Wrapper risk is minimal. `test_output_filter.py` validates the delegated implementation; packaging validation should confirm the console script resolves to this wrapper.
