# sources/storage-engines/wiredtiger/test/suite/test_verify_disagg02.py

## Purpose

`test_verify_disagg02.py` checks that verify detects duplicate btree IDs among stable files in disaggregated follower metadata.

## Important APIs, Types, and Functions

The disagg-decorated class defines leader/follower configs, layered table config, and `test_verify_duplicate_btree_ids`. It uses metadata cursors, raw access to `file:WiredTiger.wt`, regex validation, and `session.verify`.

## Control Flow

The test creates a layered table with data on the leader, checkpoints, opens a follower, advances the checkpoint, reads the stable file config to obtain an `id=...`, inserts a fake metadata key with the same config through the raw metadata file, runs verify expecting `WT_ERROR`, ignores expected metadata-corruption stderr, removes the fake entry, and closes the follower.

## State and Persistence Behavior

It deliberately corrupts follower local metadata by adding `file:fake_duplicate.wt_stable`, then cleans it up so teardown does not fail.

## Dependencies and Integration Points

Depends on disaggregated storage helpers, follower checkpoint advancement, metadata layout for stable files, raw metadata file cursor access, and verify's unique btree ID check.

## Risks and Edge Cases

The test reaches below normal metadata APIs, so metadata schema changes can affect it. Cleanup is required to keep later teardown verification healthy.

## Test Signals

Signals are a valid victim config with `id=`, verify raising `WT_ERROR`, and expected metadata corruption diagnostics.
