<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/OMSetSecretResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/OMSetSecretResponse.java

Purpose: Persists an explicitly set S3 secret for an access ID through `S3SecretManager`.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor accepts nullable `accessId`, nullable `S3SecretValue`, required `S3SecretManager`, and `OMResponse`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the secret only when the response status is `OK` and a value is present.

Control flow and persistence: On success, it chooses between `secretManager.batcher().addWithBatch(batchOperation, accessId, s3SecretValue)` for batch-capable stores and `secretManager.storeSecret(accessId, s3SecretValue)` for non-batch stores. `@CleanupTableInfo` identifies `S3_SECRET_TABLE`, although the manager may abstract the concrete backend.

Dependencies and integration: Used by S3 secret set request handling. It integrates OM double-buffer batching with the pluggable secret manager/store path.

Risks and test signals: Non-batch stores are mutated outside the OM RocksDB batch, so replay/idempotency and failure ordering need attention. Tests should cover batch and non-batch managers, null secret no-op, status-not-OK no-op, and access ID consistency with `S3SecretValue`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/OMSetSecretResponse.java -->
