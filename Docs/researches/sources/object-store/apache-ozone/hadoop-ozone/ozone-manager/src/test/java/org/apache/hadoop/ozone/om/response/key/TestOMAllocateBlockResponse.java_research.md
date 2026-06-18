# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponse.java

Purpose: Tests `OMAllocateBlockResponse` for legacy/default key layout.

Important APIs/types/functions: Extends `TestOMKeyResponse`; uses `OMAllocateBlockResponse`, protobuf `AllocateBlockResponse`, `Status.OK`, `Status.KEY_NOT_FOUND`, `getOpenKey`, `getOpenKeyTable`, `checkAndUpdateDB`, and `addToDBBatch`.

Control flow: The success test creates `OmKeyInfo`, builds an OK allocate-block response, confirms the open key is absent, adds to batch, commits, and asserts the open key exists. The error test builds a KEY_NOT_FOUND response, invokes `checkAndUpdateDB`, commits, and asserts no row was written.

State/persistence: Success writes the key info into the open key table for the current bucket layout. Error response performs no persistent mutation.

Dependencies/integration: Uses the base key response fixture for volume/bucket cache setup and replication config.

Risks/test signals: It does not verify block-location contents, only that allocation updates open-key table presence. The key behavioral signal is success versus error no-op.
