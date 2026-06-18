# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequest.java

## Purpose

`OMFileCreateRequest` handles filesystem-style file creation for non-FSO layouts. It allocates initial blocks during preExecute, validates path semantics, creates missing parent directory markers when recursive, writes the file to the open-key table, and defers final key-table materialization until commit.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` validates key name, resolves replication config from request/bucket/OM defaults, allocates initial blocks, sets modification time/data size/type/factor/key locations, generates encryption info, checks create ACLs, and assigns a unique client ID.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates bucket and path conflicts, checks recursive parent requirements, prepares `OmKeyInfo`, appends allocated blocks, enforces byte and namespace quota, writes open-key and missing-parent key-table cache entries, and returns `OMFileCreateResponse`.
- `checkDirectoryResult(...)` rejects existing files without overwrite, directory leaf conflicts, and file-in-path conflicts.
- `checkAllParentsExist(...)` enforces non-recursive parent existence.
- Request validators reject EC pre-finalization and old-client unsupported layouts.

## Control Flow And State

PreExecute allocates blocks before full DB validation, a known tradeoff called out in comments. Validate acquires the bucket write lock, gets existing key state, walks legacy key-table path state with `OMFileRequest.verifyFilesInPath`, creates missing parent directory key infos, appends the new allocated block list to open key info, quota-checks replicated preallocated size, increments namespace only for missing parents, writes the open-key table cache entry keyed by client ID, writes parent directory cache entries, and returns block/key info to the client.

## Dependencies And Integration Points

The class integrates with SCM block allocation, block token secret manager, replication config resolution, encryption metadata generation, prefix manager, `OMFileRequest`, `OMKeyRequest`, `OMFileCreateResponse`, OM metadata open-key/key tables, and create-file protocol messages.

## Risks And Test Signals

Risks include leaked preallocated blocks on later validation failure, overwrite semantics, recursive parent handling, quota calculation using required replication nodes, encryption validation, key name validation, and old-client/EC gates. Tests should cover empty root key rejection, overwrite true/false, parent file conflicts, recursive and non-recursive creates, namespace and byte quota failures, open-key cache contents, missing parent creation, block token/key location propagation, and metrics.
