# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequest.java

Purpose: `OMKeyDeleteRequest` deletes one committed key from legacy/object-store layouts. It validates the delete request, tombstones the key table entry, updates bucket quota accounting, and marks a matching hsync open key as deleted when the visible key is still associated with an hsync lease.

Important APIs and types: The class extends `OMKeyRequest` and uses `DeleteKeyRequest`, `DeleteKeyResponse`, `KeyArgs`, `OmKeyInfo`, `OmBucketInfo`, `OMKeyDeleteResponse`, `Table<String, OmKeyInfo>`, cache `CacheKey`/`CacheValue`, `OMPerformanceMetrics`, and the old-client bucket-layout validator.

Control flow: `preExecute` validates deletion-specific snapshot reserved words, normalizes the key path, stamps modification time, resolves bucket links, checks DELETE ACLs, and attaches user info. `validateAndUpdateCache` increments delete metrics, acquires the bucket lock, validates volume/bucket, loads the committed key, sets its update ID, tombstones the key-table cache entry, loads bucket info, decrements bytes and namespace with a snapshot-used flag only for non-empty keys, optionally finds the hsync open-key entry and adds `DELETED_HSYNC_KEY`, builds the delete response, audits outside the lock, and updates success/failure metrics.

State and persistence behavior: The key-table cache receives a tombstone at the transaction index. The deleted `OmKeyInfo` is passed to the response so the batch operation can move it to the deleted table as appropriate. Bucket used bytes are decremented by `sumBlockLengths`, and namespace is decremented by one. Empty keys do not contribute to snapshot-used accounting. Hsync open-key entries are not tombstoned; they are mutated with deletion metadata so later hsync/commit logic rejects them.

Dependencies and integration points: It integrates with OM locks, metadata tables, ACL checks, audit logs, delete response batch behavior, metrics, hsync metadata conventions, and the key deletion service through the response. PreExecute also depends on snapshot reserved word checks from `OmUtils`.

Risks: If an hsync open key is missing while the committed key has `HSYNC_CLIENT_ID`, the code only warns, leaving potentially inconsistent metadata. Deleting empty keys has special accounting that must match snapshot deletion semantics. The operation does not recursively delete directories in legacy path-normalizing buckets; it only handles the resolved committed key. Layout validators must protect FSO buckets from old non-FSO clients.

Test signals: `TestOMKeyDeleteRequest` and `TestOMKeyDeleteResponse` should verify key-table tombstones, deleted-table response contents, bucket byte/namespace decrement, empty-key accounting, missing-key failures, audit fields including data size and replication for files, hsync open-key metadata mutation, ACL failure behavior, and old-client bucket-layout rejection.
