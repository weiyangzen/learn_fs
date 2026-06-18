# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_output_filter.py

## Purpose

`test_output_filter.py` extensively tests `_output.py`, the generator for synthetic subunit v2 status and attachment packets.

## Important APIs, Types, and Functions

`SafeOptionParser` prevents parser exits during tests. `safe_parse_arguments` wraps `_output.parse_arguments`. `TestStatusArgParserTests` runs as scenarios over every action in `_ALL_ACTIONS`. `ArgParserTests` covers invalid option combinations and tag parsing. `StatusStreamResultTests` checks generated status events for commands with and without attachments. `FileDataTests` covers attachment-only packets. `MatchesStatusCall` is a custom matcher for `StreamResult` double event tuples.

## Control Flow

Tests parse CLI-like argument lists, run `generate_stream_results` into `testtools.testresult.doubles.StreamResult`, and match the resulting `_events`. Several tests patch `_o.create_timestamp`, `_o._CHUNK_SIZE`, and `_o.sys.stdin` to make output deterministic and exercise chunking/stdin paths.

## State and Persistence Behavior

State is in temporary files, in-memory byte streams, and patched module variables. No persistent files are written.

## Dependencies and Integration Points

It depends on `iso8601.UTC`, `testtools` matchers, `NamedTemporaryFile`, `BytesIO`, `TextIOWrapper`, and `_output` internals. It is the main test signal for `filter_scripts/subunit_output.py`.

## Risks and Test Signals

This file strongly protects CLI parsing and stream generation. It verifies one-status-only enforcement, status ids, tags, timestamps, binary attachments, empty files, stdin filenames, chunk-size behavior, metadata only on first packet, and final statuses only on the last attachment packet. It is less focused on actual byte serialization because it uses a stream-result double rather than `StreamResultToBytes`.
