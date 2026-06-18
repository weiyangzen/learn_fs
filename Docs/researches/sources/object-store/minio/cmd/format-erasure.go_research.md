<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure.go -->
# sources/object-store/minio/cmd/format-erasure.go

## Purpose
Defines erasure `format.json` schemas, migration, validation, quorum selection, disk initialization, and replacement-disk format generation. This is the persistence contract that prevents drive-order corruption and keeps erasure deployments stable across restarts and healing.

## Important APIs, types, and functions
- Constants define backend names, erasure versions, distribution algorithms, and the offline disk UUID.
- `formatErasureV1`, `formatErasureV2`, and `formatErasureV3` model historical and current `format.json` forms.
- `newFormatErasureV3`, `Drives`, and `Clone` create and copy layouts.
- `formatGetBackendErasureVersion`, `formatErasureMigrate`, `formatErasureMigrateV1ToV2`, and `formatErasureMigrateV2ToV3` upgrade old formats.
- `loadFormatErasureAll`, `loadFormatErasure`, `saveFormatErasure`, and `saveFormatErasureAll` read/write disk metadata.
- `checkFormatErasureValue`, `checkFormatErasureValues`, `formatErasureV3Check`, and `getFormatErasureInQuorum` validate format consistency.
- `initStorageDisksWithErrors`, `initFormatErasure`, `fixFormatErasureV3`, `ecDrivesNoConfig`, and `newHealFormatSets` support bootstrap and healing.

## Control flow
Bootstrap opens all endpoints concurrently, creates a reference layout, clones it for each drive with a unique `This` UUID, warns if a host has too many drives in a set, writes each format through a temporary file plus rename, and returns a quorum reference format with `This` cleared. Startup loads formats concurrently, validates version/backend/drive count/set width, then selects the majority drive count as the reference. Migration reads existing JSON, detects erasure version, upgrades V1 to V2, then V2 to V3, moving old multipart data to a trash path during V2-to-V3 migration.

## State and persistence behavior
Persistent state is `.minio.sys/format.json` on every disk. Writes are intended to be atomic at the storage layer by writing a UUID-named temp file and renaming it to `format.json`; heal writes may also persist a healing tracker. V2-to-V3 migration renames `.minio.sys/multipart` into `.minio.sys/tmp/.trash/<uuid>`.

## Dependencies and integration points
Integrates storage disks, endpoint topology, storage-class parity lookup, healing trackers, quorum reducers, logger/color warnings, filesystem migration helpers, and format consumers in `erasure-sets.go`.

## Risks and edge cases
This file is high risk: wrong quorum logic, UUID matching, set-size validation, or migration behavior can make data unavailable or accept foreign drives. `getFormatErasureInQuorum` groups by total drive count rather than a full hash, relying on later strict checks. `fixFormatErasureV3` only repairs empty `This` for local single-set migrated formats.

## Test signals
`format-erasure_test.go` covers empty `This` repair, V1-to-V3 migration, invalid format values, quorum selection/check failures, healing format generation, and benchmarks for quorum and storage initialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure.go -->
