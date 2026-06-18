# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequestWithFSO.java

## Purpose

`OMDirectoryCreateRequestWithFSO` is the filesystem-optimized directory-create implementation. It stores path components in the directory table using volume, bucket, parent object ID, and name keys instead of legacy key-table directory marker entries.

## Important APIs, Types, And Functions

- Overrides `validateAndUpdateCache(OzoneManager, ExecutionContext)`.
- Uses `OMFileRequest.verifyDirectoryKeysInPath(...)` to walk the FSO directory and file tables.
- Builds missing parent `OmDirectoryInfo` objects and the leaf `OmDirectoryInfo`.
- Writes directory cache entries with `OMFileRequest.addDirectoryTableCacheEntries(...)`.
- Returns `OMDirectoryCreateResponseWithFSO` carrying volume/bucket IDs and created directory info.

## Control Flow And State

After rejecting root creation, the request acquires the bucket write lock, validates bucket/volume, traverses the FSO path, rejects file conflicts, and either reports already-existing directory or creates missing parents plus the leaf directory. It computes `volumeId` and `bucketId`, quota-checks the number of created entries, increments bucket namespace usage, writes directory table cache entries, and returns a double-buffer response with copied bucket info.

## Dependencies And Integration Points

It relies on `OMDirectoryCreateRequest` for preExecute and shared result enum, `OMFileRequest` FSO traversal/cache helpers, `OmDirectoryInfo`, `OMDirectoryCreateResponseWithFSO`, and bucket/object ID conventions in `OMMetadataManager`.

## Risks And Test Signals

FSO correctness depends on parent object IDs and leaf object IDs. Tests should cover file conflicts in intermediate and leaf positions, existing leaf directory, missing parent creation, namespace quota, ACL inheritance from closest parent/bucket, response volume/bucket IDs, and no legacy key-table directory marker writes.
