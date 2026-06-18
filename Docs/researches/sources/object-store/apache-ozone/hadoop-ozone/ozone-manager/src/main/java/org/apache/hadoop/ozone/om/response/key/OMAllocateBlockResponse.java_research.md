# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponse.java

Purpose: `OMAllocateBlockResponse` persists newly allocated block metadata for an open key.

Important APIs and types: It extends `OmKeyResponse`, stores `OmKeyInfo` and client ID, cleans `OPEN_KEY_TABLE` and `BUCKET_TABLE`, and writes to `getOpenKeyTable(getBucketLayout())`.

Control flow: `addToDBBatch` derives the open-key name from volume, bucket, key, and client ID, then writes updated open key info.

State and persistence behavior: It updates open-key table state with additional block locations. It does not commit the key or update deleted table.

Dependencies and integration points: It is used after allocate-block request validation and SCM block allocation.

Risks and test signals: Tests should assert open-key naming, bucket layout routing, block list persistence, and failed response no-op.
