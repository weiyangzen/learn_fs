# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare01.py

## Purpose

This regression test covers WT-17257: forward iteration on a layered follower cursor after a prepared remove is rolled back. It ensures that a prepare conflict does not leave the cursor positioned such that stable keys are skipped.

## Important APIs, Types, and Functions

The class is a `disagg_test_class` with scenarios varying which stable keys receive prepared removes. `safe_next` converts a raised `WiredTigerError` containing `WT_PREPARE_CONFLICT` into the return code for direct assertion. The table is created as `type=layered` with `block_manager=disagg`.

## Control Flow

The leader writes scenario `stable_keys` at commit timestamp 100, advances stable to 200, checkpoints, and transfers the checkpoint to a follower. A follower prepare session removes `prepared_keys` in ingest and prepares at timestamp 300. A reader at timestamp 400 opens a layered cursor and expects the first `next()` to conflict. After the prepared transaction is rolled back, the same cursor continues iteration and must return every stable key in order.

## State, Persistence, and Dependencies

Persistent state includes stable checkpoint content on the leader and unresolved prepared tombstones on the follower ingest tree. The test depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`, and integrates with prepared transactions, timestamped checkpoints, follower checkpoint pickup, and layered cursor merge state.

## Risks and Test Signals

The risk is stale cursor state after a prepare conflict, especially when the prepared remove is first, middle, last, or covers multiple keys. The primary signal is that after rollback the cursor returns exactly `stable_keys` and ends with `WT_NOTFOUND`. This catches both skipped stable records and duplicate/incorrect ordering after conflict recovery.
