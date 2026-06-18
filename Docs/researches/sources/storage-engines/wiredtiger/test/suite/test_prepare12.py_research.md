# sources/storage-engines/wiredtiger/test/suite/test_prepare12.py

## Purpose

Tests update restore of a page containing a prepared update while another uncommitted update and eviction pressure are present.

## Important APIs, Control Flow, and State

The test parameterizes column and integer-row key formats. It creates a table, prepares key 1 with value `a` at timestamp 1, opens a second session with an uncommitted insert to key 2, then a third session inserts many larger records in independent transactions to fill the small cache and trigger eviction/update restore. The original prepared update is then committed with commit timestamp 1 and durable timestamp 2. A read transaction at timestamp 2 asserts key 1 returns `a`.

## Dependencies, Risks, and Test Signals

Dependencies are `wttest`, `make_scenarios`, small-cache eviction, multiple sessions, and timestamp commit/read APIs. The risk is update restore losing or misordering a prepared update when another uncommitted update exists on the page. The signal is a successful timestamp read after cache pressure and prepare commit.
