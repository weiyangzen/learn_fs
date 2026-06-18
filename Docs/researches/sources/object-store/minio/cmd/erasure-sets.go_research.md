<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets.go -->
# sources/object-store/minio/cmd/erasure-sets.go

## Purpose
Implements the multi-set erasure object layer that presents many fixed erasure sets as one `ObjectLayer`. It owns disk placement, reconnect monitoring, per-set lockers, object-name-to-set routing, fan-out operations that must span sets, and healing of missing `format.json` files on replacement disks.

## Important APIs, types, and functions
- `erasureSets` holds `sets`, reference `formatErasureV3`, protected `erasureDisks`, distributed lockers, endpoints, set geometry, pool index, distribution algorithm, and deployment ID.
- `connectEndpoint`, `findDiskIndex`, and `findDiskIndexByDiskID` validate a drive against the reference format before a `StorageAPI` is accepted into a set slot.
- `newErasureSets` builds per-set `erasureObjects`, lockers, endpoint closures, cleanup goroutines, and the background disk reconnect loop.
- `hashKey`, `sipHashMod`, `crcHashMod`, `getHashedSetIndex`, and `getHashedSet` are the object placement boundary.
- Object APIs such as `PutObject`, `GetObjectNInfo`, multipart methods, metadata/tag/tier methods, and `HealObject` delegate to the hashed set.
- `DeleteObjects`, `deletePrefix`, `StorageInfo`, `LocalStorageInfo`, `Shutdown`, and cleanup routines fan out across sets when needed.
- `HealFormat`, `formatsToDrivesInfo`, and `newHealFormatSets` integration repair fresh unformatted drives without changing established topology.

## Control flow
Startup constructs endpoint strings, lockers keyed by host, and one `erasureObjects` per set. Initial disks are placed by disk ID, then periodic `monitorAndConnectEndpoints` calls `connectDisks`, which tries only missing/offline/reconnected endpoints, loads `format.json`, checks topology, and installs the disk under `erasureDisksMu`. Normal object traffic hashes the object name using the format's distribution algorithm and forwards to exactly one set. Bulk delete groups input objects by hashed set and runs per-set deletes concurrently, while prefix force delete walks all sets. Copy optimizes metadata-only same-set copies and otherwise streams source data into the destination set.

## State and persistence behavior
The persistent authority is `format.json`: deployment ID, set UUID matrix, per-drive `This` UUID, and distribution algorithm. Runtime state includes the mutable disk matrix, local drive maps, lock clients, cleanup timers, and audit tags. `HealFormat` writes missing `format.json` files to unformatted replacement drives, records before/after drive states, updates local drive maps, and may start active write monitoring.

## Dependencies and integration points
This file integrates `StorageAPI`, `formatErasureV3`, `erasureObjects`, distributed `dsync` locks, madmin heal/storage types, global API cleanup intervals, global background heal state, audit logging, site/decommission/tiering object APIs, and endpoint/pool metadata. It also depends on SipHash/CRC for stable placement and `xsync.MapOf` for deleted bucket discovery.

## Risks and edge cases
Changing hash algorithms or deployment ID handling can move objects across sets. Incorrect disk reordering checks can accept the wrong physical drive or reject a valid replacement. `HealFormat` is sensitive to quorum, reference-format equality, unformatted/offline/corrupt distinction, and local-vs-remote reconnection behavior. Background cleanup and reconnect goroutines rely on global timers and can mask operational races if tests run with global state.

## Test signals
`erasure-sets_test.go` covers CRC/SipHash stability, invalid cardinality and unknown algorithms, creation of a 16-drive erasure set, and stable object-to-set mapping. Broader healing and object routing are mostly exercised by integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets.go -->
