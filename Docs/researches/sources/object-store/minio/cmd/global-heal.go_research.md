<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/global-heal.go -->
# sources/object-store/minio/cmd/global-heal.go

## Purpose
Implements background healing orchestration for local drives and queued bucket/object healing. It creates the reserved background heal sequence, reports local heal state, scans erasure sets, and heals objects/versions while updating trackers and global counters.

## Important APIs, types, and functions
- `bgHealingUUID` identifies the always-on background heal sequence.
- `newBgHealSequence` initializes a `healSequence` with `healDeleteDangling`.
- `getLocalBackgroundHealStatus` reports scanned counts, healing disks, set status, and storage-class parity.
- `healEntryResult` carries per-entry progress from concurrent heal workers.
- `(*erasureObjects).healErasureSet` drives bucket/object scanning and healing for one erasure set.
- `healBucket` and `healObject` enqueue work into global background heal state.

## Control flow
`healErasureSet` finds the background sequence, copies queued buckets, heals bucket metadata first, reads disk info, sizes worker concurrency from disk request capacity or config, and starts a result collector that updates the healing tracker. For each bucket it loads versioning/lifecycle/object-lock/replication state, selects online disks including the healing disk at the end, rejects insufficient non-healing disks, lists raw metadata recursively, and schedules `healEntry` workers for agreed or partial entries. Each entry skips directories and internal metacache/trash/multipart paths, resolves versions, ignores versions newer than heal start or expired by lifecycle, calls `HealObject`, checks the healed disk state, updates counters, and records progress.

## State and persistence behavior
State spans global heal sequences, healing trackers saved to disk, background scanned/healed/failed counters, queued buckets, local disk healing flags, and lifecycle expiry queues. The function persists tracker updates and may enqueue lifecycle expiry or restored-object deletion during healing.

## Dependencies and integration points
Integrates erasure metadata listing, object healing, lifecycle, object lock, replication, bucket versioning, storage-class parity, madmin heal/status types, worker pools, global heal config, global HTTP request throttling, and local storage info.

## Risks and edge cases
Healing must avoid rewriting newly uploaded versions, expired objects, internal metadata paths, and all-healing sets. Partial metadata resolution with quorum one is intentionally permissive but can surface inconsistent entries. Worker/result channel coordination and tracker updates are concurrency-sensitive. Insufficient disks or listing errors leave buckets queued for retry.

## Test signals
No direct tests in this group. Signals come from healing integration tests, madmin background-heal status, tracker persistence, successful object reconstruction, lifecycle skip behavior, and logged failures for list/heal errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/global-heal.go -->
