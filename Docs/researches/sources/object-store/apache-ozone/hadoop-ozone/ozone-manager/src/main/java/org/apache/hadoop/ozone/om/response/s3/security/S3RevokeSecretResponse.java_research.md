<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3RevokeSecretResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3RevokeSecretResponse.java

Purpose: Applies S3 secret revocation by deleting the secret associated with a Kerberos ID/access identity through `S3SecretManager`.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `kerberosID`, required `S3SecretManager`, and `OMResponse`. `addToDBBatch` is the only behavior and is guarded by non-null ID plus `Status.OK`.

Control flow and persistence: For batch-capable secret storage, the delete is added to the OM batch with `s3SecretManager.batcher().deleteWithBatch`. Otherwise it invokes `s3SecretManager.revokeSecret(kerberosID)` directly. Cleanup table metadata identifies `S3_SECRET_TABLE`.

Dependencies and integration: Used by revoke-secret request handling and abstracted secret storage implementations.

Risks and test signals: Direct non-batch deletion is outside RocksDB atomicity. Tests should cover batch and non-batch stores, repeated revoke idempotency, status-not-OK no-op, and null Kerberos ID behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3RevokeSecretResponse.java -->
