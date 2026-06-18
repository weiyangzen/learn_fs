# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMOpenKeysDeleteResponse.java

Purpose: `OMOpenKeysDeleteResponse` moves stale open keys/open files to the deleted table during open-key cleanup.

Important APIs and types: It extends `AbstractOMKeyDeleteResponse`, stores a map from open key name to `(bucketId, OmKeyInfo)`, and cleans open-key/open-file, deleted, and bucket tables.

Control flow: `addToDBBatch` gets the open-key table for the bucket layout and calls `addDeletionToBatch` for each open key with `isCommittedKey=false`.

State and persistence behavior: It deletes open-key/open-file rows and writes non-empty uncommitted key parts to deleted table for block cleanup.

Dependencies and integration points: It integrates open key cleanup service, bucket layout routing, and key deletion service.

Risks and test signals: Tests should cover stale open key deletion, empty open key skip, committed flag false, FSO/default layouts, and failed response no-op.
