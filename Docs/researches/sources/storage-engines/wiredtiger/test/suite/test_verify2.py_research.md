# sources/storage-engines/wiredtiger/test/suite/test_verify2.py

## Purpose

`test_verify2.py` targets API verify edge cases around dirty trees, checkpoint requirements, empty-tree search behavior, and nonexistent tables.

## Important APIs, Types, and Functions

The class `test_verify2` defines table constants and three tests: `test_verify_ckpt`, `test_verify_search`, and `test_verify_empty`. It uses `session.verify`, timestamps, cursor search, `raisesBusy`, and ENOENT checking.

## Control Flow

`test_verify_ckpt` creates a table, sets stable timestamp, inserts data, expects verify to fail busy before checkpoint, checkpoints, then verifies successfully. `test_verify_search` searches an empty table for a missing key and verifies without checkpoint to ensure search did not dirty the btree. `test_verify_empty` verifies a nonexistent URI and expects ENOENT.

## State and Persistence Behavior

The tests focus on in-memory dirty state versus checkpoint-clean state. Stable timestamp is set before operations to satisfy timestamped-table expectations.

## Dependencies and Integration Points

Depends on `WT_SESSION.verify`, checkpoint dirty-clean transitions, cursor search behavior on deleted empty pages, and Python exception helpers.

## Risks and Edge Cases

It is API-only and does not cover utility behavior. The busy expectation depends on verify refusing dirty content.

## Test Signals

Signals are EBUSY before checkpoint, success after checkpoint, success after empty search without checkpoint, and ENOENT for missing object.
