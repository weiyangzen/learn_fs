# sources/storage-engines/wiredtiger/test/suite/test_prepare43.py

## Purpose

Ensures checkpoint cursors still walk pages containing prepared tombstones and do not skip keys after eviction.

## Important APIs, Control Flow, and State

The test runs under fuzzy checkpoint and precise/preserve-prepared configurations. It inserts keys 1 to 99 at timestamp 21, prepares removal of all keys at timestamp 25 with a prepared ID, advances stable beyond the prepare timestamp, checkpoints, then force-evicts the page with `ignore_prepare=true`. A checkpoint cursor on `checkpoint=WiredTigerCheckpoint` iterates from key 1 to 99 and expects every key to return the original committed value.

## Dependencies, Risks, and Test Signals

Dependencies are `make_scenarios`, checkpoint cursors, debug page eviction, and preserve-prepared base behavior. The risk is page walks incorrectly skipping pages or keys because prepared tombstones are present. The test signal is complete ordered checkpoint-cursor iteration.
