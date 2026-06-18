# sources/user-network-fs/samba/source4/torture/drs/python/replica_sync.py

## Purpose
`replica_sync.py` is a broad blackbox suite for `DsReplicaSync` and `samba-tool drs replicate` behavior. It verifies enabled/disabled inbound replication, forced replication, local replication, DN conflict resolution, LostAndFound placement, rename sequencing, deletion propagation, and reanimation conflicts.

## Important APIs, Types, And Functions
- `DrsReplicaSyncTestCase` extends `drs_base.DrsBaseTestCase`.
- `_create_ou()` creates OUs below a test root and returns object GUIDs.
- `_check_deleted()` searches by GUID with `show_deleted:1` and verifies tombstone location under Deleted Objects.
- `reanimate_object()` removes `isDeleted` and replaces `distinguishedName` to simulate object reanimation.
- Base helpers drive inbound replication settings and `samba-tool drs replicate` invocations.

## Control Flow
Setup creates a top-level OU and forces initial two-way sync. Simple tests toggle inbound replication and verify normal, blocked, forced, and local replication. Conflict tests disable inbound replication on both DCs, create same-DN objects or rename collisions with sleeps to force timestamp ordering, replicate in a chosen direction, and assert which GUID receives a `CNF:<guid>` conflict RDN. Cleanup deletes by GUID and forces replication so both sides see tombstones. Later tests cover LostAndFound when children arrive under deleted parents, complex rename ordering across parent moves, and a reanimated tombstone colliding with a new object.

## State And Persistence Behavior
The suite creates and deletes OUs on both DCs, disables inbound replication, and restores it in teardown. It tracks two primary GUIDs in `self.ou1` and `self.ou2`, with additional child GUIDs scoped to tests. Deletion checks explicitly inspect tombstones rather than merely absence, ensuring replicated delete metadata is present.

## Dependencies And Integration Points
It depends on Samba test OU helpers, LDB GUID binding syntax, `samba-tool drs replicate`, and base helpers for LostAndFound and Deleted Objects DNs. It exercises replication conflict algorithms, local replication mode, full-sync override behavior, high-watermark behavior indirectly, and command-line error reporting for disabled sinks.

## Risks
Conflict winner expectations depend on time ordering, so the tests use `time.sleep(1)` and can be timing-sensitive on slow or clock-skewed environments. Some tests print diagnostic names, which is useful but noisy. Because many tests disable replication, teardown restoration is essential. Name conflicts are intentional and must be isolated under the per-test root OU.

## Test Signals
Signals include `WERR_DS_DRA_SINK_DISABLED` for non-forced disabled inbound replication, successful forced/local replication, exact `CNF:<guid>` naming of losing objects, non-placement in LostAndFound for simple conflicts, placement in LostAndFound for orphaned children, RDN/name equality after conflict resolution, and tombstones under Deleted Objects on both DCs after cleanup replication.
