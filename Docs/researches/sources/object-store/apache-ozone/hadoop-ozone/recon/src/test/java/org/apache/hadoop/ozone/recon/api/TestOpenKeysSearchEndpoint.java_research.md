# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenKeysSearchEndpoint.java

## Purpose
Tests `OMDBInsightEndpoint.getOpenKeyInfo` as a search endpoint for open keys. The fixture emphasizes path-prefix validation, bucket-or-deeper search requirements, FSO directory traversal, OBS and Legacy open-key lookup, result limits, pagination cursors, and empty or missing paths.

## Important APIs, Types, And Functions
The file uses `OMDBInsightEndpoint.getOpenKeyInfo`, `KeyInsightInfoResponse`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `NSSummaryTaskWithFSO`, and OM metadata helper writers `writeDirToOm`, `writeOpenFileToOm`, and `writeOpenKeyToOm`. Helper methods create volumes, buckets, directories, FSO open files, and non-FSO open keys with generated positive object IDs.

## Control Flow
`setUp` creates OM metadata, a Recon injector, and a namespace summary manager; it populates an FSO hierarchy, OBS bucket keys, Legacy bucket keys, and empty buckets; then it reprocesses FSO namespace summaries. Tests call `getOpenKeyInfo(limit, prevKey, startPrefix, includeFso, includeNonFso)` for root, volume, bucket, directory, nested directory, exact key, missing path, limit-only, bad request, and cursor combinations.

## State And Persistence
All data is written to temporary OM tables. FSO files use object IDs and parent IDs in the open file table, while OBS and Legacy entries use flat open key table keys. Bucket metadata stores layouts and used bytes. Namespace summaries persist parent-child relationships needed to search beneath FSO directories.

## Dependencies And Integration Points
This test exercises endpoint path parsing against OM bucket layouts, FSO namespace summary traversal, open file/open key tables, and pagination state represented by `prevKey` and `lastKey`. It uses Recon SQL and container DB infrastructure through the injector even though the tested behavior is mostly OM metadata search.

## Risks
Search behavior is tightly coupled to normalized path strings and table key ordering. The bad-request contract rejects root and volume-level prefixes, while empty `prevKey` and empty `startPrefix` can still return global results in specific cases. Refactors to prefix validation, pagination cursor format, or FSO summary traversal can affect many assertions.

## Test Signals
Signals include 400 responses for root and volume prefixes, 204 no-content responses for non-existent bucket/directory/key searches, exact counts for FSO bucket and nested directory searches, replicated size equal to three times unreplicated size for RATIS data, limited result counts, and stable `lastKey` values across pages.
