# sources/storage-engines/wiredtiger/test/suite/test_layered_schema10.py

## Purpose

This suite tests the publish API on followers and schema step-up behavior. Schema operations queued while a node is a follower must be replayed correctly when that node becomes leader, and then flushed to shared metadata only when the stable schema epoch reaches their publish epoch.

## Important APIs, Types, and Functions

Helpers set stable schema epochs on arbitrary connections, run leader checkpoints, publish URIs, compute stable constituent URIs, check local metadata via cursor-open, check shared metadata via `file:WiredTigerShared.wt_stable`, seed an initial epoch checkpoint, swap roles, open followers, and checkpoint/advance back to the original connection. `suite_subprocess` isolates an expected panic for split create/drop epochs.

## Control Flow

Tests cover follower-created tables becoming locally available after role swap, create-then-drop on a follower leaving no trace, follower-created data becoming visible to the old leader after checkpoint pickup, multiple follower-created tables published at different epochs flushing independently, follower drops removing shared metadata only after the drop epoch, unpublished follower creates never flushing, and schema-epoch-only advancement forcing a checkpoint to run. The split-epochs subprocess creates and drops a table at different epochs before step-up; checkpointing at the intermediate epoch is expected to panic because the table should be visible but its stable constituent was never created.

## State, Persistence, and Dependencies

State includes follower metadata queues, local metadata, shared metadata, role reconfiguration, stable schema epoch, transactional stable timestamps, checkpoint pickup, and skip-checkpoint connection close behavior. Dependencies include `wiredtiger`, `wttest`, `helper_disagg`, `suite_subprocess`, and `wtscenario`.

## Risks and Test Signals

Risks include losing follower-queued schema operations on step-up, flushing operations at the wrong epoch, treating unpublished operations as publishable, skipping checkpoints when only schema epoch advances, and mishandling create/drop pairs. Signals are explicit local/shared metadata assertions after role swaps and checkpoint pickups, plus a subprocess nonzero exit for the intentional API-violation panic.
