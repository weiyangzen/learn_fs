# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_tags.py

## Purpose

`subunit_tags.py` applies tag additions or removals to every test event in a subunit v2 stream.

## Important APIs, Types, and Functions

`main()` calls `subunit.tag_stream(sys.stdin, sys.stdout, sys.argv[1:])`. Tags are expressed as `TAG` to add or `-TAG` to remove.

## Control Flow

The command delegates all parsing and rewriting to `tag_stream`, which reads v2 packets and rewrites `test_tags` before serializing them to stdout.

## State and Persistence Behavior

State is limited to the tag set transformation in `tag_stream`. It writes a transformed stream to stdout and persists no files.

## Dependencies and Integration Points

It depends on the public `subunit.tag_stream` helper. It is useful in pipelines where CI wants to annotate or strip tags without re-running tests.

## Risks and Test Signals

Risk is mostly stream mode: stdin/stdout must be binary-safe through `tag_stream`. `test_subunit_tags.py` validates both adding and removing tags while preserving the rest of the v2 stream.
