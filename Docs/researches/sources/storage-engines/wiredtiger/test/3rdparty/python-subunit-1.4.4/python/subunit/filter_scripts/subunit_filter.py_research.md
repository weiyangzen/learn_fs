# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_filter.py

## Purpose

`subunit_filter.py` filters subunit v2 streams by outcome, tags, regular expressions, expected-failure lists, and optional test id renaming.

## Important APIs, Types, and Functions

`make_options()` defines filtering flags: include/exclude errors, failures, successes, skips, xfails, passthrough behavior, tag filters, `--with`/`--without` regex filters, `--fixup-expected-failures`, `--only-genuine-failures`, and `--rename`. `_make_regexp_filter()` builds a predicate over test id, outcome, error, and details. `_compile_rename()` returns chained `re.sub` renaming. `_make_result()` creates a `TestResultFilter` wrapped through extended/stream decorators to emit v2. `main()` combines regexp and tag predicates and calls `filter_by_result`.

## Control Flow

The command parses options, builds predicate functions, reads expected-failure ids with `read_test_list`, and streams input through the v2 filter path. `TestResultFilter` decides per-test whether buffered start/tags/outcome/stop calls should be forwarded. Passthrough defaults to forwarding non-subunit input as v2 stdout packets unless disabled.

## State and Persistence Behavior

State is in filter predicates, expected-failure sets, and `TestResultFilter` buffering for the current test. No persistent files are written unless stdout is redirected by the caller.

## Dependencies and Integration Points

It depends on `re`, `optparse`, `testtools` stream decorators, `subunit.StreamResultToBytes`, shared `filter_by_result` and `find_stream`, and `subunit.test_results` filter helpers. It is the CLI front-end for the result filtering classes.

## Risks and Test Signals

Regex filters concatenate stringified test, outcome, error, and details, so filtering can match implementation-specific detail text. `--rename` mutates test objects by replacing their `id` method. `test_subunit_filter.py` covers default success stripping, tag filtering, no-passthrough, passthrough, expected-failure fixups, renames, preserved time ordering, and command execution through `python -m`.
