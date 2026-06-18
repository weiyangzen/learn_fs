# sources/storage-engines/wiredtiger/test/suite/test_layered_schema02.py

## Purpose

This test ensures that a follower dropping a layered table does not fall back to reading the stable table from a checkpoint. After a follower-side drop, opening the logical table must fail even though stable data may exist in shared storage.

## Important APIs, Types, and Functions

The class uses `disagg_test_class`, a leader connection, and a manually opened follower. It writes `nitems * 3` string records, advances a checkpoint to the follower, uses `drop(..., force=true)` on the follower, and later reopens the leader connection before dropping the leader table.

## Control Flow

The leader and follower create the same layered table. The leader writes three key prefixes for 10,000 indices, checkpoints, and the follower picks up the checkpoint. The follower scans to confirm all data is visible, drops the table with force, and verifies opening the cursor now raises `WiredTigerError`. The leader is then scanned to prove its table still has data, reopened to avoid cached-handle effects, dropped, and similarly verified inaccessible.

## State, Persistence, and Dependencies

State spans leader data, follower stable checkpoint visibility, follower local schema metadata, and leader schema after reopen. Dependencies are `os`, `wiredtiger`, `wttest`, and `helper_disagg`. The integration points are layered drop, checkpoint pickup, cursor open failure behavior, and local-vs-shared metadata precedence.

## Risks and Test Signals

The key risk is a dropped follower table resurrecting from shared stable metadata. Signals include row-count validation before drop and expected cursor-open failures after follower and leader drops. The large row count gives a meaningful scan signal that checkpoint pickup worked before the drop assertion.
