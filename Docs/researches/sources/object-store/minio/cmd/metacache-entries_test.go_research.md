# sources/object-store/minio/cmd/metacache-entries_test.go

## Purpose

`metacache-entries_test.go` validates core metacache entry algorithms: sortedness, marker forwarding, sorted merge behavior, object/prefix filters, directory containment, and quorum-based metadata resolution. It is the strongest direct test coverage for `metacache-entries.go`.

## Important Tests And Control Flow

The early tests load sample metacache entries and check that `sort` repairs ordering, `forwardTo` positions at exact and prefix-like markers, `merge` preserves duplicate names when metadata differs, and filters produce expected object-only, prefix-only, recursive, root-recursive, custom-separator, and prefix-filtered name lists. `Test_metaCacheEntry_isInDir` table-tests root, direct file, direct directory, and deeper path semantics.

`Test_metaCacheEntries_resolve` constructs multiple `xlMetaV2` inputs with different version IDs, modtimes, signatures, zero version IDs, empty version sets, and delete markers. It serializes them into `metaCacheEntry` values and runs a large table over strict/non-strict modes and different object/directory quorum values. Each case is shuffled repeatedly to ensure deterministic resolution independent of input order. Expected outputs include selected single entries, merged multi-version results, delete-marker handling, and below-quorum failures.

## Risks And Test Signals

The tests provide strong signals for resolution semantics and filter outputs. Gaps include `mergeEntryChannels` concurrency/cancellation, metadata pool reuse, `fileInfos`/`fileInfoVersions` delimiter behavior under versioning config, corrupted xl.meta decode paths, and lifecycle/replication side effects in list filtering.
