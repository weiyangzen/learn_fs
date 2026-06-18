# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_tags.py

## Purpose

`test_subunit_tags.py` verifies `subunit.tag_stream`, which adds or removes tags from v2 status packets.

## Important APIs, Types, and Functions

`TestSubUnitTags` creates `BytesIO` original and filtered streams. `test_add_tag` writes inprogress and success packets with tags, applies `["quux"]`, and compares against several acceptable byte encodings because tag set order can vary. `test_remove_tag` writes tags including `bar`, applies `["-bar"]`, and compares against a reference stream without `bar`.

## Control Flow

Tests serialize v2 packets with `StreamResultToBytes`, rewind input, invoke `tag_stream`, and compare resulting bytes.

## State and Persistence Behavior

Only in-memory streams are used. No files are persisted.

## Dependencies and Integration Points

It depends on `testtools`, `Contains` matcher, public `subunit`, and `subunit.test_results` importability. It covers the implementation used by `filter_scripts/subunit_tags.py`.

## Risks and Test Signals

The add-tag test accounts for non-deterministic set ordering in serialized bytes. These tests strongly protect binary stream fidelity for tag transformations but do not cover global non-test attachments or empty tag sets.
