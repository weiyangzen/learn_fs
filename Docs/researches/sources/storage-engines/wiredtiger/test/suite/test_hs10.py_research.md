# sources/storage-engines/wiredtiger/test/suite/test_hs10.py

## Purpose

Regression test for reading modify histories correctly after eviction forces the original page out of cache.

## Important APIs, Types, and Functions

Defines `test_hs10` with `get_stat` and `test_modify_insert_to_hs`, using small cache, one eviction thread, and column/integer row scenarios.

## Control Flow

It writes a base value and three timestamped modifies, checkpoints, fills another table with many records to force eviction of the first table, then reads key 1 at timestamps 3, 4, and 5 through different cursors.

## State and Persistence Behavior

State is a single-key modify chain persisted through checkpoint and later reloaded from HS/data-store after cache pressure.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, scenario generation, timestamped reads, and cache pressure from a second table.

## Risks and Maintenance Signals

The extra-table writes rely on cache pressure instead of an explicit eviction stat. `get_stat` is unused.

## Test Signals

Signals are exact reconstructed values `value1+A`, `value1+AB`, and `value1+ABC` after eviction pressure.
