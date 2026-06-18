# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_filter.py

## Purpose

`test_subunit_filter.py` validates both the `TestResultFilter` class and the `subunit.filter_scripts.subunit_filter` command.

## Important APIs, Types, and Functions

`TestTestResultFilter` uses a sample v1 subunit stream containing global/local tags, pass, fail, error with details, skip, and xfail. It tests default success filtering, tag filters, per-test tag scope, excluding each outcome type, expected-failure fixups, unexpected success fixup, custom predicates with old and new signatures, time ordering, skip preservation, and id renaming. `TestFilterCommand` executes `python -m subunit.filter_scripts.subunit_filter` as a subprocess and decodes v2 output.

## Control Flow

Class-level helper `run_tests` feeds bytes through `ProtocolTestCase` into a result filter. Command tests build v2 streams with `StreamResultToBytes`, run the module subprocess with stdin/stdout pipes, and decode output with `ByteStreamToStreamResult`.

## State and Persistence Behavior

State is in in-memory streams and subprocess execution. No persistent files are used.

## Dependencies and Integration Points

It depends on `subprocess`, `sys.executable`, `unittest`, `iso8601`, `testtools` doubles, public subunit stream adapters, and `TestResultFilter`/`make_tag_filter`. It directly covers the CLI filter and shared result filtering logic.

## Risks and Test Signals

This is a high-value regression suite for preserving filtered stream semantics. It specifically protects time passthrough for filtered tests, tag scoping, passthrough encoding of non-subunit input, and command default behavior. The subprocess tests also validate module importability and packaging layout.
