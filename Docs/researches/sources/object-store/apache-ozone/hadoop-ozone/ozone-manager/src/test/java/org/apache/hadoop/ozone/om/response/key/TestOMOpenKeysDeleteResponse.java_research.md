# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMOpenKeysDeleteResponse.java

Purpose: Tests `OMOpenKeysDeleteResponse` for cleaning expired/open keys in default and FSO layouts.

Important APIs/types/functions: Parameterizes `BucketLayout.DEFAULT` and `FILE_SYSTEM_OPTIMIZED`; uses `OMOpenKeysDeleteResponse`, `Pair<Long, OmKeyInfo>` bucket-object mapping, `getOpenKeyTable`, `deletedTable`, `getOzoneDeletePathKey`, and `OMRequestTestUtils` open-key/file helpers.

Control flow: For each layout, helper methods create open keys directly in DB. Empty-block test deletes a selected subset and verifies those open rows are removed without deleted-table entries while other open rows remain. Non-empty-block test adds block info and verifies deleted rows move to `deletedTable`. Error test uses INTERNAL_ERROR and confirms no mutation.

State/persistence: Mutates open key/open file tables and, for block-bearing keys, deleted table. Deletion map is per-open-key DB key with bucket object ID and key info.

Dependencies/integration: Integrates layout-specific open-key naming, FSO parent IDs, bucket creation, and block metadata handling.

Risks/test signals: Uses random parent IDs for FSO without creating directory rows. Test checks first deleted key info committed flag is false for open-key cleanup, distinguishing it from committed-key deletion.
