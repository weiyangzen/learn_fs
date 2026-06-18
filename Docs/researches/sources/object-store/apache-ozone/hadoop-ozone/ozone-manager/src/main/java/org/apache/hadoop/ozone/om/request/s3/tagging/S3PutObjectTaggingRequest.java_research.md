
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequest.java

Purpose: Handles S3 `PutObjectTagging` for non-FSO bucket layouts by validating the key path, resolving bucket links/ACLs, and replacing the `OmKeyInfo` tag map without changing object content metadata.

Important APIs and types: Extends `OMKeyRequest`; uses `PutObjectTaggingRequest`, `KeyArgs`, `KeyValueUtil.getFromProtobuf`, `OmKeyInfo`, `OMMetadataManager.getKeyTable`, `S3PutObjectTaggingResponse`, and `BUCKET_LOCK`.

Control flow: `preExecute` normalizes the key name, resolves bucket and write ACLs, and rewrites the request. `validateAndUpdateCache` increments metrics, takes the bucket write lock, validates volume and bucket, loads the key table entry by ozone key, throws `KEY_NOT_FOUND` when absent, builds a new `OmKeyInfo` with tags and update ID, adds it to the key-table cache, returns a success response, audits, and records failure metrics/logs on exceptions.

State and persistence behavior: The only persistent mutation is a key-table cache update at the Ratis transaction index. The key modification time is deliberately not changed because S3 last-modified tracks object content changes, not tag changes.

Dependencies and integration points: Integrates S3 gateway tagging RPCs with OM key metadata, ACL checks, audit logging, lock tracking, double-buffer response persistence, and `OMClientRequestUtils.shouldLogClientRequestFailure`.

Risks: Correctness depends on the resolved `KeyArgs` from `preExecute` matching the cache update path. Missing key handling is explicit, but tag-size or tag-count policy is assumed to have been validated before this handler. Tests should cover existing key, absent key, ACL rejection, audit/failure metric paths, and unchanged modification time.
