<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure.go -->
# sources/object-store/minio/cmd/erasure.go

## Purpose
Defines the single erasure-set object layer state and shared utilities for disk status, storage info, online-disk selection, cleanup, and namespace scanning. It is the per-set implementation that `erasureSets` composes and routes object operations into.

## Important APIs, types, and functions
- `erasureObjects` stores set geometry, pool/set indexes, disk/locker/endpoint closures, and namespace lock map.
- `defaultWQuorum` and `defaultRQuorum` compute write/read quorums from data/parity layout.
- `diskErrToDriveState`, `getDisksInfo`, `getOnlineOfflineDisksStats`, and `getStorageInfo` translate storage errors and metrics into admin API structures.
- `getOnlineDisksWithHealingAndInfo` orders usable disks before scanning and healing disks.
- `cleanupDeletedObjects` removes `.minio.sys/tmp/.trash` contents on local disks using deadline workers and dynamic sleepers.
- `nsScanner` performs bucket data-usage scanning, cache loading/saving, bucket randomization, per-disk worker scheduling, and periodic update publication.

## Control flow
Administrative calls snapshot the current disk slice from the closure and query disks concurrently. Disk selection shuffles indexes, records errors, filters offline/healing disks, and orders non-scanning disks before scanning and optional healing disks. The namespace scanner loads the prior root cache, randomizes bucket order with new buckets first, starts a saver goroutine that periodically emits cache clones, bounds scanner parallelism by `GOMAXPROCS`, and runs `NSScanner` on selected disks while preserving per-bucket cache state.

## State and persistence behavior
Persistent state includes data-usage cache files saved through the erasure object layer and `.trash` directories removed from local drive paths. Runtime state is mostly closures into the parent `erasureSets`, disk health snapshots, and scanner channels. Storage-info output exposes disk UUIDs, mount paths, inode stats, healing/scanning flags, and per-API metrics.

## Dependencies and integration points
This file integrates `StorageAPI`, endpoint metadata, `madmin` disk/storage structures, MinIO disk scanners, data-usage cache types, global drive and cleanup configs, namespace locking, and error quorum reducers used by bucket metadata operations.

## Risks and edge cases
Quorum formulas affect availability semantics. Disk state translation must distinguish offline, corrupt, unformatted, permission, faulty, and root-mount conditions. Scanner correctness depends on consuming the update channel, saving final state on close, and not scanning only healing disks. The utilization calculation uses integer division before conversion, which may under-report non-100% usage.

## Test signals
Direct tests in this group focus on erasure encode/decode setup rather than these admin/scanner paths. The main signals come from integration tests that inspect admin disk states, scanner data-usage caches, healing behavior, and storage info output.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure.go -->
