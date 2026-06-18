# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequest.java

## Purpose

`OMDirectoryCreateRequest` handles directory creation for non-FSO bucket layouts by representing directories as key-table entries. It creates missing parent directories when needed and enforces filesystem path conflict rules.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` normalizes request metadata, rejects snapshot reserved words, sets modification time, resolves bucket links, and checks `CREATE` ACLs.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates bucket/volume, rejects root directory creation, verifies files/directories in path, creates missing parent `OmKeyInfo` entries, creates the leaf directory key, checks namespace quota, and returns `OMDirectoryCreateResponse`.
- `Result` captures `SUCCESS`, `DIRECTORY_ALREADY_EXISTS`, and `FAILURE`.
- Validators reject EC configs before finalization and block old clients from operating on unsupported bucket layouts.

## Control Flow And State

The request acquires the bucket write lock, calls `OMFileRequest.verifyFilesInPath`, rejects file conflicts, treats existing directory as idempotent `DIRECTORY_ALREADY_EXISTS`, and for missing paths builds directory key info plus missing parent info using inherited `OMKeyRequest` helpers. It increments bucket used namespace by missing parents plus leaf directory and writes key-table cache entries through `OMFileRequest.addKeyTableCacheEntries`. Auditing and metric logging occur after lock release.

## Dependencies And Integration Points

The class integrates with `OMKeyRequest` helpers for key info, ACL inheritance and quota checks, `OMFileRequest` path verification/cache utilities, `OMDirectoryCreateResponse`, OM metadata tables, bucket layout validators, and OM metrics/audit.

## Risks And Test Signals

Tests should cover root path rejection, file-in-path conflicts, existing directory idempotency, recursive missing-parent creation, namespace quota accounting, ACL inheritance, FSO/legacy layout validator behavior, EC pre-finalization rejection, and cache entries for parent directories and leaf directory.
