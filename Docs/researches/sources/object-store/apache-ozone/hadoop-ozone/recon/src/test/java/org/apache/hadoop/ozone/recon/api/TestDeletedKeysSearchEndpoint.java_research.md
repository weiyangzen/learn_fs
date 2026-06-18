# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestDeletedKeysSearchEndpoint.java

## Purpose
This JUnit test validates deleted-key search through `OMDBInsightEndpoint.getDeletedKeyInfo`. It covers root/volume restrictions, empty search, bucket/directory/key-level prefixes, nested directories, limits, bad requests, last-key calculation, pagination, empty buckets, and combinations of `prevKey` and `startPrefix`.

## Important APIs and functions
`setUp` creates an empty OM metadata manager, imports it into Recon OM, builds a Recon injector with SQL and container DB support, gets `OMDBInsightEndpoint`, then calls `populateOMDB`. `populateOMDB` writes 16 deleted keys across `volb/bucketb1` and `volc/bucketc1` with nested directory-like key names. `createDeletedKey` builds deleted table keys shaped as `/volume/bucket/key/random` and stores `RepeatedOmKeyInfo`. `writeDeletedKeysToOm` writes directly to the OM deleted table.

## Control flow, state, and persistence
The test persists deleted key rows into Recon OM metadata. Endpoint calls use `limit`, `prevKey`, and `startPrefix` to seek and filter table entries. Tests assert HTTP statuses and `KeyInsightInfoResponse` list sizes, last-key prefixes, and first returned key names after cursor skips.

## Dependencies and integration points
Dependencies include Recon OM metadata, `OMDBInsightEndpoint`, `KeyInsightInfoResponse`, OM `RepeatedOmKeyInfo`, `OmKeyInfo`, standalone replication config, and `ReconTestInjector`. The endpoint likely feeds Recon UI insight pages for deleted/pending-deletion key browsing.

## Risks and edge cases
The fixture is path-string based and does not create volume/bucket table entries for every prefix, so the endpoint behavior under real metadata validation may differ if validation is added. A key named `filgetec6` appears in the fixture and may be intentional noise or typo. Bad request tests for negative limit assert the path error message rather than a limit-specific error. Deleted keys include random suffixes, so tests compare counts and prefixes rather than exact keys.

## Test signals
Strong coverage for prefix filtering and cursor semantics, including empty prefix full-table scans. It protects user-visible pagination behavior through `lastKey` and the "No keys matched" `NO_CONTENT` contract.
