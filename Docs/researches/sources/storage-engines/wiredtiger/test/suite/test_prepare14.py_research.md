# sources/storage-engines/wiredtiger/test/suite/test_prepare14.py

## Purpose

Tests visibility for an on-disk update whose start and stop time points come from the same uncommitted prepared transaction.

## Important APIs, Control Flow, and State

The test runs for in-memory and non-in-memory configurations and column/integer-row keys. It creates a timestamp-capable table, optionally disables logging for in-memory, pins timestamps to 10, and in a separate session inserts then removes the same key before preparing at timestamp 20. A debug `release_evict` cursor reads with `ignore_prepare=true`, expects `WT_NOTFOUND`, resets to force eviction, and a second read again expects not found.

## Dependencies, Risks, and Test Signals

Dependencies are cursor remove, prepared transactions, debug eviction, and `WT_NOTFOUND`. The risk is an insert/remove pair in a prepared transaction becoming visible or being restored incorrectly after eviction. Signals are successful eviction of a prepared start-stop chain and repeated not-found reads under `ignore_prepare`.
