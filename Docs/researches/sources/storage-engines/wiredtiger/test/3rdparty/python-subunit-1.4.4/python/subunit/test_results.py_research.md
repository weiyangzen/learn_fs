# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/test_results.py

## Purpose

`test_results.py` provides reusable `TestResult` and `StreamResult` helpers for timing, tag collapsing, filtering, listing, per-test callbacks, CSV output, and attachment passthrough.

## Important APIs, Types, and Functions

`TestResultDecorator` forwards extended result calls while degrading through `testtools.ExtendedToOriginalDecorator`. `HookedTestResultDecorator` adds `_before_event` hooks. `AutoTimingTestResultDecorator` injects timestamps unless explicit time events are seen. `TagsMixin`, `TagCollapsingDecorator`, and `TimeCollapsingDecorator` coalesce tag/time events.

`make_tag_filter()` and `and_predicates()` build predicates. `_PredicateFilter` buffers current-test events until it knows whether a test passes the predicate. `TestResultFilter` builds outcome predicates, expected-failure fixups, and optional id renaming. `TestIdPrintingResult` prints test ids and optional durations from result or stream events. `TestByTestResult` calls an `on_test` callback with status, times, tags, and details at stop. `CsvResult` writes rows from that callback. `CatFiles` is a `StreamResult` that writes file attachment bytes to a stream.

## Control Flow

Decorators forward most calls directly. Hooked decorators call `_before_event` before non-time/progress events. `_PredicateFilter.startTest` begins buffering; outcome calls either buffer or mark the test filtered; `stopTest` replays buffered calls to a decorated result only if the test was not filtered. `TestResultFilter` first applies renames and expected-failure transformations, then delegates to `_PredicateFilter`.

`TestIdPrintingResult.status` supports v2 stream events: `exists` can be printed when requested, `inprogress` starts duration tracking, and final statuses print the id and duration. `TestByTestResult` stores outcome details and calls the callback when `stopTest` arrives.

## State and Persistence Behavior

All state is per-result in memory: tags, buffered calls, active tests, durations, counters, start/stop timestamps, and details. Output classes write text rows or raw bytes to supplied streams. No files are opened here.

## Dependencies and Integration Points

It depends on `csv`, `datetime`, `iso8601`, `testtools`, `TracebackContent`, `text_content`, and public `subunit.make_stream_binary`. It is used by filter scripts, `subunit.run`, stats/listing commands, and passthrough routing.

## Risks and Test Signals

Important risks include preserving event ordering when filtering, not leaking per-test tags globally, handling explicit versus automatic time, mutating `test.id` during renames, and byte/text stream mismatches in `CsvResult` or `CatFiles`. There are small suspicious duplications, such as `TestIdPrintingResult.addError` incrementing `failed_tests` twice. Tests in this subset cover filters, stats, tags, CSV indirectly, listing indirectly, and time ordering through `test_subunit_filter.py`.
