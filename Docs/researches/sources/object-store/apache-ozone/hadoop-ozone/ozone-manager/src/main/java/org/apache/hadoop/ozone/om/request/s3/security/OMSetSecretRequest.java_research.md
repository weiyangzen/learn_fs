## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/OMSetSecretRequest.java

Purpose: `OMSetSecretRequest` handles setting/replacing an existing S3 secret key for an access ID. It validates access ID existence, secret validity, and caller permission, then updates the S3 secret manager cache under the access ID lock.

Important APIs/types/functions: `preExecute` checks tenant access ID table, legacy S3 secret table, secret non-empty/minimum length, and `S3SecretRequestHelper.checkAccessIdSecretOpPermission`. `validateAndUpdateCache` uses `ozoneManager.getS3SecretManager().doUnderLock`, `S3SecretValue.of(accessId, secretKey, context.getIndex())`, `updateCache`, and `OMSetSecretResponse`.

Control flow: PreExecute rejects unknown access IDs unless they exist in the old secret table, rejects empty or too-short secrets, builds/fetches a UGI from the access ID, and enforces owner/admin permission. Validate/update locks the secret manager entry, rechecks the legacy secret exists before update, writes a new `S3SecretValue` to cache, builds a response containing access ID and secret key, and logs/audits success or failure.

State and persistence behavior: The request updates the S3 secret manager cache at the transaction index. It targets the legacy S3 secret table path and throws `ACCESS_ID_NOT_FOUND` if the secret manager has no existing secret row during update. The response carries the manager and value for replay/flush behavior.

Dependencies and integration points: It integrates S3 secret management with tenant access ID metadata, legacy S3SecretTable compatibility, secret manager locking, audit under `OMAction.SET_S3_SECRET`, and tenant-aware permission helper logic.

Risks and edge cases: The request requires an existing secret in the secret manager at update time even if preExecute saw a tenant access ID, so migrated/new tenant rows without legacy secret entries can fail. The response includes the secret key, so logging/audit must avoid exposing secret material beyond intended response fields. Minimum length validation is client-visible.

Test signals: Cover setting valid existing secrets, missing access ID, tenant access ID without secret manager row, empty/short secret rejection, owner/admin permission, non-owner rejection, cache update ID, and audit fields.
