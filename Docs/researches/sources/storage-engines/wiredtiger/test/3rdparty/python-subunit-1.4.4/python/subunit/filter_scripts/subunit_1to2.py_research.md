# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_1to2.py

## Purpose

`subunit_1to2.py` converts a subunit v1 stream into a subunit v2 byte stream.

## Important APIs, Types, and Functions

`make_options()` returns a basic `OptionParser`. `main()` opens stdin or the named input file with `find_stream`, wraps stdout in `StreamResultToBytes`, adapts it with `ExtendedToStreamDecorator`, and passes the v1 input through `run_tests_from_stream`.

## Control Flow

The conversion relies on the v1 parser in `ProtocolTestCase`/`TestProtocolServer`, which emits extended result events. `ExtendedToStreamDecorator` maps those events into v2 `status` calls, and `StreamResultToBytes` serializes them.

## State and Persistence Behavior

This is a pure streaming transformation from input to stdout. It persists no state and exits 0 after conversion.

## Dependencies and Integration Points

It depends on `testtools.ExtendedToStreamDecorator`, `subunit.StreamResultToBytes`, and shared filter helpers. It is paired with `subunit_2to1.py` for protocol migration.

## Risks and Test Signals

Fidelity risks include v1 features that do not map perfectly to v2 stream status packets. Regression tests should round-trip representative v1 streams with details, tags, time, progress, and passthrough text.
