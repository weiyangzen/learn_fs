# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_tap2subunit.py

## Purpose

`test_tap2subunit.py` validates TAP-to-subunit conversion for many TAP plan, outcome, directive, comment, and missing-test cases.

## Important APIs, Types, and Functions

`TestTAP2SubUnit` uses `StringIO` TAP input and `BytesIO` subunit output. Each test writes TAP text, calls `subunit.TAP2SubUnit`, and checks decoded v2 events through `ByteStreamToStreamResult`. `UTF8_TEXT` documents the expected text attachment MIME type.

## Control Flow

The tests cover whole-file skip plans (`1..0`), unnamed and numbered `ok` tests, descriptions, `SKIP`/`skip` directives with comments, `TODO` directives mapped to xfail, bailouts mapped to fail, missing tests from plans or skipped numbers, trailing plans, no-plan streams, leading/trailing comments attached as `tap comment`, and mixed TODO/SKIP behavior.

## State and Persistence Behavior

State is in in-memory streams. No persistent files are used.

## Dependencies and Integration Points

It depends on `testtools.TestCase`, `testtools.compat._u`, `StreamResult` double, and public `subunit.TAP2SubUnit`. It directly protects `filter_scripts/tap2subunit.py`.

## Risks and Test Signals

This is the main compatibility signal for TAP conversion. It verifies exact event tuples including test ids, statuses, runnable flags, attachment names, bytes, EOF, MIME type, and timestamp absence. It does not cover all TAP dialect extensions, but it covers the package's supported grammar well.
