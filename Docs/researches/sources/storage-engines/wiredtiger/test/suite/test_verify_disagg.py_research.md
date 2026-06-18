# sources/storage-engines/wiredtiger/test/suite/test_verify_disagg.py

## Purpose

`test_verify_disagg.py` verifies `SESSION.verify` semantics for disaggregated layered tables across leader and follower roles, including transient follower metadata/checkpoint states and history-store population.

## Important APIs, Types, and Functions

The disagg-decorated class uses scenarios for history-store fill and storage backends. Helpers include `leader_put_data`, `verify`, and `create_follower`; test methods cover normal leader/follower verify, missing leader table, follower without metadata, and follower without checkpoint.

## Control Flow

The main test creates a layered table on a leader, verifies empty state, creates a follower, checks ENOENT before checkpoint pickup, checkpoints and advances follower checkpoint, writes multiple timestamped generations, expects EBUSY for dirty leader data, checkpoints, advances the follower, and verifies both roles.

## State and Persistence Behavior

State spans leader/follower WiredTiger homes, disaggregated checkpoint metadata, layered stable/ingest components, optional history-store records, and timestamps.

## Dependencies and Integration Points

Depends on `helper_disagg` class decoration, generated disaggregated storage scenarios, `disagg_advance_checkpoint`, layered table block manager, timestamped commits, and verify's role-aware behavior.

## Risks and Edge Cases

Follower transient states are subtle: no metadata should return ENOENT, while a locally created layered URI without stable checkpoint should verify successfully by tolerating missing stable state. Dirty leader data must remain rejected.

## Test Signals

Signals are verify success/failure matching role and checkpoint state, ENOENT for missing metadata/table, EBUSY for dirty leader content, and successful follower verification after checkpoint advancement.
