# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithLegacy.java

## Purpose
Comprehensive REST-level test for `NSSummaryEndpoint` over `LEGACY` buckets. It mirrors the FSO namespace scenario while using legacy key naming and filesystem-path configuration, validating that basic info, disk usage, replicated size, quota usage, file-size distribution, and full-path construction work for legacy OM tables.

## Important APIs, types, and functions
- Endpoint APIs under test are the same namespace summary surfaces: basic info via shared helpers, `getDiskUsage`, `getQuotaUsage`, and `getFileSizeDistribution`.
- Legacy fixture setup uses `getMockOzoneManagerServiceProvider`, `setConfiguration`, `OZONE_OM_ENABLE_FILESYSTEM_PATHS`, and `NSSummaryTaskWithLegacy.reprocessWithLegacy`.
- Directory writes use legacy-style key names ending in `OM_KEY_PREFIX`, and key writes use full key paths with `BucketLayout.LEGACY` and default parent id behavior.
- Replication tests use `OmKeyLocationInfoGroup`, `BlockID`, mocked container replica sets, `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `QuotaUtil`.
- `ReconUtils.constructFullPath` is tested for legacy keys where parent object ID is not populated and the key name already carries the path.

## Control flow
`setUp` configures OM metadata with filesystem paths enabled, creates Recon services, populates the legacy namespace, adds the `vol3/bucket5` Ratis subtree, overlays multi-block replicated keys, and runs legacy summary reprocessing. Tests then exercise shared basic-info behavior, DU at root/volume/bucket/directory/key levels, invalid paths, replica-aware sizes, quota usage, file-size distributions, legacy full-path construction, and Ratis replication calculations for `vol3`, `bucket5`, and `dir6`.

## State and persistence behavior
Unlike FSO, legacy directory and key hierarchy is primarily encoded in key names such as `dir1/dir2/file2` and directory marker keys ending with the OM key prefix; parent IDs are mostly set to zero/default in fixture writes. Derived namespace summaries are persisted by `NSSummaryTaskWithLegacy`. Replica-aware DU depends on the same mocked six-container replica map as FSO, while factor-three Ratis keys under `vol3` validate replication-config-based size calculations. Quota state is stored on volume and bucket table rows, and mocked SCM root stats provide root capacity/usage values.

## Dependencies and integration points
The test connects legacy OM key-table semantics, filesystem-path configuration, Recon namespace summary task logic, endpoint path parsing, shared summary assertions, SCM replica lookup, and quota/stat utilities. Its parity with the FSO suite is valuable because it protects a common REST contract across two different metadata layouts.

## Risks and edge cases
The fixture has duplicated expected-size arithmetic and must stay aligned with the FSO twin. Legacy path construction is less parent-ID dependent, so it does not cover rebuild-in-progress negative parent behavior the same way FSO does. Some replica assertions depend on the first returned DU child. The mocked SCM replica model covers replica counts but not datanode health, EC keys, or container lifecycle variations.

## Test signals
Signals include layout-specific basic-info expectations for `BucketLayout.LEGACY`, exact DU counts/sizes, invalid-path and non-applicable quota statuses, replica-aware size totals from root down to keys, Ratis factor-three size checks, quota usage at root/volume/bucket levels, file-size-bin counts, and full-path construction directly from legacy key names.
