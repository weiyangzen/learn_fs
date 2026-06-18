# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponseWithFSO.java

Purpose: Tests `OMDirectoryCreateResponseWithFSO` for FILE_SYSTEM_OPTIMIZED layout, including path-ID keying and bucket namespace update.

Important APIs/types/functions: Uses `OMDirectoryCreateResponseWithFSO`, `OMDirectoryCreateRequestWithFSO.Result.SUCCESS`, `OmDirectoryInfo`, `getOzonePathKey(volumeId,bucketId,parentID,name)`, `directoryTable`, `volumeTable`, `bucketTable`, and cache entries.

Control flow: Setup creates OM metadata and a batch. The test adds a volume and bucket to DB cache for ID lookups, creates an `OmDirectoryInfo` with explicit object/parent IDs, builds a successful `CreateDirectory` response, constructs the FSO response with volume/bucket IDs, calls `addToDBBatch`, commits, and verifies the directory and bucket rows.

State/persistence: Writes one row to `directoryTable` keyed by numeric volume ID, bucket ID, parent ID, and directory name. Writes bucket info with `usedNamespace` to `bucketTable`.

Dependencies/integration: Integrates FSO object-ID lookup, cache-backed volume/bucket metadata, and directory-table persistence.

Risks/test signals: Uses a synthetic `parentID` not created in `directoryTable`, so it verifies response DB writes rather than full path validation. Missing `@AfterEach` close for the batch is a minor lifecycle asymmetry in this file.
