# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponseWithFSO.java

Purpose: FSO specialization of bulk key delete response, including directory deletion behavior when the bucket has already been deleted.

Important APIs/types/functions: Uses `OMKeysDeleteResponseWithFSO`, `OMFileRequest.getOmKeyInfo`, `OmDirectoryInfo`, `deletedDirTable`, `OMBucketDeleteResponse`, FSO `directoryTable`/key table, and volume ID.

Control flow: Overrides prerequisites to create an FSO directory, convert it to an `OmKeyInfo` for directory deletion, and create ten file keys under the bucket. Inherited success/failure tests delete file keys. Additional test simulates bucket deletion by adding a tombstone cache entry and committing `OMBucketDeleteResponse`, then runs bulk delete and asserts file rows and directory rows are removed while deleted-dir entries are created for deep cleanup.

State/persistence: Removes rows from FSO key table and directory table. When bucket is gone, directory metadata is written into `deletedDirTable` under object-ID-qualified delete keys.

Dependencies/integration: Integrates FSO table helpers, bucket deletion response, cache tombstones, and deleted-dir cleanup semantics.

Risks/test signals: Files have no blocks, so deleted-table behavior for block cleanup is not tested. The bucket-deleted path is a specialized cleanup scenario with manual cache tombstoning.
