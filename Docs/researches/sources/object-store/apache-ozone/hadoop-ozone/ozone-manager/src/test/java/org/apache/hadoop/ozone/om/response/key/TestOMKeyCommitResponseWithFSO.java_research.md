# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponseWithFSO.java

Purpose: FSO specialization of key commit response tests.

Important APIs/types/functions: Uses `OMKeyCommitResponseWithFSO`, `getOzonePathKey`, `getOpenFileName`, `OzoneFSUtils.getFileName`, `OMRequestTestUtils.addFileToKeyTable`, FSO object/parent IDs, and delete maps keyed by `getOzoneDeletePathKey`.

Control flow: Overrides response construction to include volume ID and FSO delete-key mapping, creates FSO `OmKeyInfo` with bucket object ID as parent, preloads open file table with `addFileToKeyTable`, and computes final FSO DB path. Inherited success, error no-op, and overwrite tests execute against FSO tables.

State/persistence: Moves an open file row to `keyTable(FILE_SYSTEM_OPTIMIZED)` and optionally writes overwritten file versions to `deletedTable`.

Dependencies/integration: Depends on base fixture volume/bucket cache, FSO key table helpers, and file-name extraction.

Risks/test signals: Parent directory is represented by bucket object ID; nested directories are not modeled. Delete-map branch references the class field `keysToDelete`, so null handling is tied to inherited test setup.
