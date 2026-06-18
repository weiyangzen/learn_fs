# sources/storage-engines/wiredtiger/test/suite/test_layered_schema11.py

## Purpose
Tests disaggregated layered schema checkpoint pickup when a follower has locally dropped a table that still exists in shared metadata from an older leader checkpoint.

## APIs, Types, And Functions
Defines `test_layered_schema11`, decorated with `@disagg_test_class`, using `gen_disagg_storages(..., disagg_only=True)`. Helper APIs cover `Connection.set_timestamp` for `stable_disaggregated_schema_epoch`, `Session.checkpoint`, `Session.publish` with `schema_epoch`, `disagg_advance_checkpoint`, metadata cursors on `file:WiredTigerShared.wt_stable`, and local cursor-open probes on stable-file URIs.

## Control Flow, State, And Persistence
The tests create layered tables, publish CREATE or REMOVE entries at schema epochs, checkpoint with stable epochs before or after drops, and then advance a follower checkpoint. State is split across leader shared metadata, follower local metadata, and the follower's schema operation queue. The key persistence behavior is that deferred REMOVE entries suppress recreation from shared metadata until the leader epoch advances enough to remove the table globally.

## Dependencies, Integration, Risks, And Test Signals
Integrates disaggregated helper storage, layered table metadata naming, publish epochs, and checkpoint metadata pickup. Risks are stale shared metadata, per-table isolation bugs, and incorrect handling of REMOVE followed by CREATE for the same URI. Assertions check presence or absence in local and shared metadata after each checkpoint advance.
