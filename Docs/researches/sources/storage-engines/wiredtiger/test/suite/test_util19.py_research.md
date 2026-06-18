# sources/storage-engines/wiredtiger/test/suite/test_util19.py

## Purpose

`test_util19.py` validates `wt downgrade` compatibility behavior across combinations of initial creation release and requested downgrade release.

## Important APIs, Types, and Functions

The class defines scenario matrices for `create_release` and `downgrade_release`, `conn_config` to set initial compatibility/logging, and `test_downgrade` to populate records and inspect downgrade verbose output.

## Control Flow

For each scenario, the test opens a logging-enabled database, optionally with `compatibility=(release=...)`, inserts 100 records, runs `wt -C <config> downgrade -V <release>` without reopening the session, and checks whether verbose log compatibility text appears.

## State and Persistence Behavior

The command mutates database compatibility metadata and log compatibility state. Log files are retained to exercise downgrade compatibility transitions.

## Dependencies and Integration Points

Depends on compatibility configuration, the `wt downgrade` utility, logging compatibility levels, `verbose=[log]`, and scenario expansion.

## Risks and Edge Cases

The assertion checks verbose text rather than querying metadata directly. Exact compatibility-version mapping must stay synchronized with WiredTiger release rules.

## Test Signals

Expected signals are downgrade success and presence or absence of `WT_CONNECTION.reconfigure: ... COMPATIBILITY: Version now <n>` according to the target release.
