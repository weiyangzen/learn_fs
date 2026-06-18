# sources/storage-engines/wiredtiger/test/suite/test_layered_schema03.py

## Purpose

This suite validates that dropping layered tables removes local metadata, prevents cursor opens, updates shared metadata correctly, and does not crash later sweep. It covers both `layered:` creation and `table:` with `block_manager=disagg,type=layered`.

## Important APIs, Types, and Functions

Helpers `check_metadata_entry`, `check_shared_metadata`, and `validate_drop` inspect `metadata:`, `file:WiredTigerShared.wt_stable`, and cursor-open behavior. Connection config enables statistics logging and fast file-manager close scanning. Scenarios combine table prefix/type with disaggregated storage.

## Control Flow

`test_create_drop` creates, populates, checkpoints, drops, validates local metadata removal, checkpoints again, and checks shared metadata no longer contains the table. `test_create_drop_checkpoint` does the same through a custom session that is closed to release dhandle references for sweep. `test_create_drop_follower` creates and checkpoints on leader, reopens as a follower using checkpoint metadata, drops locally, validates local removal, checkpoints, and expects shared metadata still to contain the table because a follower drop should not erase the leader's shared metadata.

## State, Persistence, and Dependencies

The tests persist local metadata, shared metadata, data files, and dhandle lifecycle through checkpoint and sweep. Dependencies include `re`, `os`, `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and `wiredtiger.stat`.

## Risks and Test Signals

Risks include stale metadata entries, incorrect shared metadata removal on followers, cursor access to dropped tables, and sweep crashes from closed handles. Signals are direct metadata `WT_NOTFOUND` checks, shared metadata containment checks, expected cursor-open failures, and successful completion after checkpoint/sweep-sensitive paths.
