# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2disk.py

## Purpose

`subunit2disk.py` is the command shim for exporting a subunit v2 stream to filesystem artifacts.

## Important APIs, Types, and Functions

`main()` simply returns `to_disk()` from `subunit._to_disk`. The module imports `sys` only to call `sys.exit(main())` in its executable block.

## Control Flow

All parsing, stream decoding, and file writing are delegated to `_to_disk.to_disk`. This module exists to provide a stable module/entry-point name.

## State and Persistence Behavior

State and persistence are owned by `_to_disk`. This wrapper creates no additional state.

## Dependencies and Integration Points

It integrates packaging console entry points and `python -m subunit.filter_scripts.subunit2disk` with the actual exporter implementation.

## Risks and Test Signals

Risks are minimal in the wrapper. `test_filter_to_disk.py` validates the underlying command path by calling `_to_disk.to_disk`; packaging tests should also confirm the console script points here.
