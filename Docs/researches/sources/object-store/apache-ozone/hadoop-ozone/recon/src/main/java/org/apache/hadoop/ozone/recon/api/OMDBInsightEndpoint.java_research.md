<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/OMDBInsightEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/OMDBInsightEndpoint.java

## Purpose

`OMDBInsightEndpoint` backs Recon's key insight APIs under `/keys`: open keys/files, open MPU summary, pending-deletion keys/directories, deleted directory summary, and filtered key listing.

## Important APIs and Types

Important endpoints include `/open`, `/open/summary`, `/open/mpu/summary`, `/deletePending/summary`, `/deletePending`, `/deletePending/dirs`, `/deletePending/dirs/summary`, and `/listKeys`. It uses `KeyInsightInfoResponse`, `ListKeysResponse`, `KeyEntityInfo`, `ReconBasicOmKeyInfo`, `ParamInfo`, and OM table types including `OmKeyInfo` and `RepeatedOmKeyInfo`.

## Control Flow

Open-key listing validates bucket-level `startPrefix`, scans non-FSO open keys from the legacy open-key table if requested, then scans FSO open files after converting name paths to object-id paths and recursively gathering subpaths from namespace summaries. Deleted-key listing scans the deleted table with prefix/prevKey pagination. Deleted-directory listing delegates to `ReconGlobalMetricsService`. `/listKeys` requires bucket-level or deeper prefixes, gates on OM initialization, then scans legacy and FSO basic key tables with filters for replication type, creation date, and size.

## State and Persistence

The endpoint writes no state. It reads Recon's OM RocksDB mirror, global stats table, and namespace summary table. Pagination state is returned through `lastKey` and accepted as `prevKey`.

## Dependencies and Integration Points

It integrates with `ReconOMMetadataManager`, `ReconGlobalStatsManager`, `ReconNamespaceSummaryManagerImpl`, `ReconGlobalMetricsService`, `BucketHandler`, `ReconUtils`, and `ReconResponseUtils`. It shares FSO path semantics with namespace handlers.

## Risks and Edge Cases

The endpoint mutates `ParamInfo.startPrefix` while scanning FSO subpaths, so callers must not reuse the object expecting the original prefix. `prevKey` is consumed across non-FSO and FSO scans in `/open`, which can make mixed-layout pagination subtle. `validateStartPrefix` only checks bucket-level shape, not existence. `convertStartPrefixPathToObjectIdPath` can throw `NullPointerException` if volume or bucket lookup returns null. `retrieveKeysFromTable` limits by total `results.size`, so prior legacy results constrain FSO scans.

## Test Signals

Coverage should include open-key filtering combinations, invalid start prefixes, FSO directory recursion, empty and no-match responses, deleted table pagination, deleted-dir summary, list-key filters, creation-date parsing through `ParamInfo`, service-not-ready handling, and pagination across mixed legacy/FSO results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/OMDBInsightEndpoint.java -->
