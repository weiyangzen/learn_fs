# sources/storage-engines/wiredtiger/test/suite/test_eviction04.py

## Purpose

Checks reconciliation performs in-memory restoration when eviction encounters invisible updates.

## Important APIs, Types, and Functions

Defines `test_eviction04`, `conn_config`, `get_stat`, and `test_eviction`, using data-source stat `cache_write_restore_invisible`.

## Control Flow

One session commits key 1, then starts but does not commit key 2. Another debug cursor evicts the page positioned at key 1. The test asserts reconciliation restored invisible content in memory.

## State and Persistence Behavior

State includes a committed update, an uncommitted/invisible update, and an eviction-triggered reconciliation pass. The uncommitted transaction is committed after the stat check.

## Dependencies and Integration Points

Depends on `wttest`, `wiredtiger.stat`, statistics logging, and debug cursor `release_evict`. Skipped for disaggregated mode.

## Risks and Maintenance Signals

It is stat-based and assumes debug eviction succeeds. It tests a minimal single-page scenario rather than broad workloads.

## Test Signals

Signal is data-source `cache_write_restore_invisible` greater than zero after eviction.
