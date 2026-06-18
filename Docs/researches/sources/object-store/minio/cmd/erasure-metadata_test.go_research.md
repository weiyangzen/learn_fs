# sources/object-store/minio/cmd/erasure-metadata_test.go

Purpose: unit coverage for the metadata helpers that maintain `FileInfo` part layout, choose quorum-consistent metadata, compare transition state, handle tier-free-version markers, and compute per-object parity/quorum.

Important APIs and functions under test: `FileInfo.AddObjectPart`, `objectPartIndex`, `FileInfo.ObjectToPartOffset`, `findFileInfoInQuorum`, `FileInfo.TransitionInfoEquals`, `SetSkipTierFreeVersion`/`SkipTierFreeVersion`, `listObjectParities`, and `commonParity`. It uses `newFileInfo`, `UTCNow`, `mustGetUUID`, storage-class-sized erasure metadata, and lifecycle transition fields.

Control flow: tests build synthetic `FileInfo` arrays with controlled erasure indexes, modtimes, parts, successor modtimes, version counts, transition metadata, and invalid entries. `TestFindFileInfoInQuorum` uses helper-generated arrays to validate both quorum failures and secondary-property quorum overlays. `TestListObjectParities` constructs tiered and non-tiered cases across 15- and 16-disk layouts to assert the difference between simple-majority tiered metadata quorum and EC data-block quorum.

State and persistence behavior: all state is in memory. The tests do not initialize disks except through synthetic `FileInfo` values, making them fast and tightly scoped to pure metadata behavior.

Dependencies and integration points: integrates with the same metadata primitives consumed by `erasure-object.go` and `erasure-multipart.go`. The tests encode assumptions about `humanize.MiByte` part sizes, lifecycle transition complete semantics, invalid erasure indexes, and the `InsufficientReadQuorum` error type.

Risks: tests assert type class for `InsufficientReadQuorum` rather than full error internals in some places, so changes to quorum reason classification may need additional coverage. `ObjectToPartOffset` accepts a negative offset case as valid in the current logic, which is an unusual behavior and should be preserved only if all callers constrain public ranges beforehand.

Test signals: strong regression signals for sorted part insertion, replacement of existing parts, offset-to-part mapping boundaries, quorum threshold behavior, secondary version summary propagation, transition metadata equality, and parity derivation for transitioned objects.
