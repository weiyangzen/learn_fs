# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequest.java

Purpose: `OMKeySetTimesRequest` updates a key modification time for non-FSO layouts. It ignores access time, validates ACLs in preExecute, and writes a new key-table cache value with an updated transaction ID.

Important APIs and types: The class extends `OMKeyRequest` and uses `SetTimesRequest`, `SetTimesResponse`, `KeyArgs`, `OmKeyInfo`, `OMKeySetTimesResponse`, bucket locks, cache `CacheKey`/`CacheValue`, `IAccessAuthorizer.ACLType.WRITE_ACL`, and audit action `SET_TIMES`.

Control flow: The constructor snapshots volume, bucket, key, and mtime from the original request. `preExecute` normalizes the key path, resolves bucket links, checks WRITE_ACL on the key when ACLs are enabled, audits preExecute ACL failures, and writes normalized key args and mtime back into the request. `validateAndUpdateCache` rejects mtime less than `-1`, acquires the bucket lock, builds the ozone key, loads the key-table row, fails if missing, applies the mtime when non-negative, sets update ID, writes the key-table cache entry, returns a success response, releases the lock, and audits completion.

State and persistence behavior: Only the key-table row is updated. `mtime == -1` results in operation success without changing modification time, but still updates the cache entry and update ID after `apply` is called. Bucket quota and namespace are unchanged. The response carries the updated `OmKeyInfo` for batch persistence.

Dependencies and integration points: It depends on key path normalization, bucket-link resolution, ACL infrastructure, bucket locks, audit logging, response batch behavior, and subclasses overriding response construction for FSO. It shares volume/bucket/key getters and hook methods with the FSO variant.

Risks: The constructor stores fields before preExecute normalization and bucket-link resolution; request lifecycle must create the transaction object from the pre-executed request for fields to match normalized args. The method does not call `validateBucketAndVolume` directly, so missing bucket manifests through key lookup/lock behavior rather than the common validation path. `mtime == -1` semantics can surprise callers expecting no update ID change.

Test signals: `TestOMSetTimesRequest` should cover successful mtime update, `-1` no-mtime-change behavior, invalid negative mtime failure, missing-key failure, key-table cache updates with transaction index, ACL failure auditing in preExecute, normalized path handling, and response success flag.
