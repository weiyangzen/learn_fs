# sources/storage-engines/wiredtiger/test/suite/test_layered_follower15.py

## Purpose

This test validates layered follower reads when a `MODIFY` update depends on an on-disk base value that may be garbage-collection eligible in the follower ingest tree. It covers both single-key and multi-key pages, cursor `next()` and `search()`, and the case where the base value must remain readable across its visibility window.

## Important APIs, Types, and Functions

The class is decorated with `disagg_test_class` and runs over `gen_disagg_storages(..., disagg_only=True)` scenarios. It configures leader and follower connections with `statistics=(all),precise_checkpoint=true` and `disaggregated=(role=...)`. Helpers create matching leader/follower layered tables, commit timestamped items, apply `wiredtiger.Modify`, set stable timestamps on both connections, checkpoint the leader, advance the follower checkpoint, and force follower eviction through a debug `release_evict_page` session.

## Control Flow

`setup_single_key_chain` creates a value at timestamp 10, optionally makes it orphanable by advancing stable to 11, applies a long modify at 20, writes a full replacement at 30, checkpoints, advances the follower, and evicts the key. The tests then read from the follower's ingest file URI at timestamps 15, 25, and 30. The multi-key setup places neighbors on the same page so the target key's modify reconstruction can be checked against neighboring data.

## State, Persistence, and Dependencies

The test persists update chains through stable timestamp movement, checkpoints, disaggregated checkpoint pickup, and forced eviction. It depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`. It integrates with layered URI creation, ingest file cursor access, timestamped transactions, modify reconstruction, checkpoint metadata transfer, eviction, and `verifyLayered` teardown constraints.

## Risks and Test Signals

The main risk is reconstructing a modify against the wrong base: either a pruned base, a neighbor key's value, or an incorrectly visible base. The assertions check exact values, key order, neighbor survival preconditions, `WT_NOTFOUND` at scan end, and visibility at multiple read timestamps. The teardown advances stable and checkpoints to avoid verification failures from deliberately pinned timestamps.
