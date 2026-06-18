# sources/storage-engines/wiredtiger/test/suite/test_hs13.py

## Purpose

Tests reverse modify traversal after eviction when an older snapshot should reconstruct the first modified value despite newer modifies and full updates.

## Important APIs, Types, and Functions

Defines `test_hs13` with one method using `wiredtiger.Modify`, two sessions, and debug eviction.

## Control Flow

The test inserts a large value, applies a modify that prepends `A`, confirms another session sees it, starts that session's transaction, then applies a second modify and a full replacement. After evicting the page, the older transaction searches key 1 and must still see `A + value1`.

## State and Persistence Behavior

State is a historical snapshot anchored before later updates, plus HS/reverse-delta state created by eviction of the page.

## Dependencies and Integration Points

Depends on scenario key formats, modify API, cursor snapshots, and `release_evict`.

## Risks and Maintenance Signals

`value3` is unused. The regression is narrow but targets a historically delicate reverse-modify traversal path.

## Test Signals

Signal is exact older value after eviction despite newer modify/full-update chain.
