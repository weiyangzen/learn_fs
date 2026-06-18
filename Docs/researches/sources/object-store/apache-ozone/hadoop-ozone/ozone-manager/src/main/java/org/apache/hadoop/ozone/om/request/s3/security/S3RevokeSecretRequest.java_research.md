## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3RevokeSecretRequest.java

Purpose: `S3RevokeSecretRequest` revokes an S3 secret for an access ID by invalidating its secret manager cache/table entry if it exists.

Important APIs/types/functions: `preExecute` reads `RevokeS3SecretRequest.kerberosID`, builds/fetches a UGI via `S3SecretRequestHelper.getOrCreateUgi`, enforces permission, and recomposes a clean revoke request preserving command/client/trace fields. `validateAndUpdateCache` uses `S3SecretManager.doUnderLock`, `hasS3Secret`, `invalidateCacheEntry`, and `S3RevokeSecretResponse`.

Control flow: After permission validation, update acquires the per-access-ID secret manager lock. If a secret exists, it invalidates the cache entry and returns status `OK`. If no secret exists, it returns status `S3_SECRET_NOT_FOUND` and a response with null key. IOException creates an error response.

State and persistence behavior: Revocation is represented as a cache invalidation/tombstone in the secret manager at the current transaction context. The response carries the revoked access ID only when an entry existed. No bucket/key metadata is touched.

Dependencies and integration points: It integrates with S3 secret manager locking, tenant-aware permission checks, OM audit under `OMAction.REVOKE_S3_SECRET`, and protobuf status reporting.

Risks and edge cases: Missing secrets are not exceptions but status responses. PreExecute does not set user info in the recomposed request, so downstream audit relies on existing request/user handling. Permission must be checked before revealing existence where required.

Test signals: Cover revoking existing and missing secrets, cache invalidation, response status, permission failures, trace preservation, audit fields, and IOException error response.
