# sources/storage-engines/wiredtiger/test/suite/test_util17.py

## Purpose

`test_util17.py` smoke-tests the `wt stat` utility at both connection and table scopes. It checks that plausible statistics are emitted without performing detailed statistic validation.

## Important APIs, Types, and Functions

`test_stat_process` creates a table, runs `wt stat`, and checks for connection-level `cursor: cursor create calls=` output. It then runs `wt stat table:<name>` and checks a cache-walk root-page line.

## Control Flow

After table creation, the test invokes the utility twice with different arguments and inspects a fixed output file for expected substrings.

## State and Persistence Behavior

The table metadata and initial empty btree provide the target for data-source statistics. Utility output is persisted to `wt-stat.out`.

## Dependencies and Integration Points

Depends on `suite_subprocess`, the `wt stat` command, statistics cursor formatting, and cache-walk statistics availability.

## Risks and Edge Cases

The cache-walk string can be brittle across statistic naming or output-format changes. This is a smoke test, not a semantic validation of stat values.

## Test Signals

Signals are nonempty statistic output containing known connection and table statistic labels.
