## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OmKeysDeleteRequestWithFSO.java

Purpose: `OmKeysDeleteRequestWithFSO` adapts the multi-key delete request for file-system-optimized buckets, including recursive bucket deletion flows where requested paths may resolve to files or directories. It extends `OMKeysDeleteRequest` and changes lookup, cache invalidation, and response construction to use FSO path IDs and directory-table semantics.

Important APIs/types/functions: Key methods are `getOmKeyInfo`, `addKeyToAppropriateList`, `getOzoneKeyStatus`, `markKeysAsDeletedInCache`, and `getOmClientResponse`. It depends on `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OMMetadataManager.getOzonePathKey`, key/open-key/directory tables, `OmBucketInfo`, `OmKeyInfo`, `ErrorInfo`, and `OMKeysDeleteResponseWithFSO`.

Control flow: The inherited delete request gathers candidate `OmKeyInfo` values, while this subclass resolves each path through FSO status lookup. Files go into the normal key deletion list; directories go into a separate directory list. During cache update it recomputes DB keys from volume ID, bucket ID, parent object ID, and file name, then invalidates key-table or directory-table cache entries at the transaction log index. It also updates each deleted object update ID before response construction.

State and persistence behavior: Deletes are staged through metadata cache tombstones, not direct table writes. File entries are invalidated in the layout-specific key table, directory entries in the directory table, and bucket quota release is computed from block lengths. If a file has `HSYNC_CLIENT_ID` metadata, the corresponding open file entry is marked with `DELETED_HSYNC_KEY=true` and added to `openKeyInfoMap` so the response can later clean hsync open state. Missing hsync open keys are logged as potentially inconsistent DB state.

Dependencies and integration points: This request integrates recursive delete with FSO directory/file tables, open-key cleanup for hsync, quota accounting, and the specialized FSO delete response that carries deleted files, directories, bucket copy, volume ID, and open-key metadata.

Risks and edge cases: Correctness depends on using object IDs instead of flat key names; a wrong parent ID or file name would tombstone the wrong FSO row. Directory and file separation is essential because directories live outside the key table. Hsync handling tolerates missing open keys but indicates DB inconsistency. Partial delete responses must preserve per-key error details and set `OK` versus `PARTIAL_DELETE` consistently.

Test signals: Relevant tests should cover deleting files and directories in FSO buckets, recursive deletion with mixed entries, partial delete error reporting, quota release, empty-key counting, hsync-open-key deletion marking, and response replay through `OMKeysDeleteResponseWithFSO`.
