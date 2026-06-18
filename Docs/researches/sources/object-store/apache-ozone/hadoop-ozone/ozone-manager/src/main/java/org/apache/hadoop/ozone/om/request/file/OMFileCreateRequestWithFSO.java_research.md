# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequestWithFSO.java

## Purpose

`OMFileCreateRequestWithFSO` is the FSO variant of file creation. It stores parent directories in the directory table and stores the open file under an object-ID-based open-file key while keeping the user-visible full key path in the response.

## Important APIs, Types, And Functions

- Overrides `validateAndUpdateCache(...)` while inheriting block allocation, key normalization, encryption, and ACL preExecute behavior from `OMFileCreateRequest`.
- Uses `OMFileRequest.verifyDirectoryKeysInPath(...)` for FSO traversal.
- Uses `prepareFileInfo(...)` to create file `OmKeyInfo` with leaf object ID and parent object ID.
- Writes open-file entries with `OMFileRequest.addOpenFileTableCacheEntry(...)`.
- Writes missing parents with `OMFileRequest.addDirectoryTableCacheEntries(...)`.
- Returns `OMFileCreateResponseWithFSO`.

## Control Flow And State

The method rejects empty key names, locks the bucket, validates bucket/volume, calculates volume and bucket IDs, traverses the directory/file tables, loads existing file info for overwrite, validates conflicts and parent existence, prepares missing parent directory infos, resolves replication, prepares file info, appends allocated blocks, checks byte and namespace quotas, writes the open-file cache entry, writes missing directory cache entries, and returns network key info using the original full key path.

## Dependencies And Integration Points

It depends on `OMFileRequest` FSO helpers, `OmDirectoryInfo`, `OmKeyInfo`, `OzoneConfigUtil`, `OMFileCreateResponseWithFSO`, FSO metadata manager key builders, and `OMKeyRequest` helpers for quota/encryption/file info preparation.

## Risks And Test Signals

Tests should validate parent object ID use, leaf-name versus full-path key-name handling, overwrite existing file lookup, recursive missing directory creation, namespace metric count for missing parents only, no final file-table entry before commit, open-file cache key composition, quota failures, and file/directory conflict detection.
