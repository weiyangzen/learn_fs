# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3GetSecretRequest.java

Purpose: tests `S3GetSecretRequest` and related S3 secret lifecycle behavior, including secret creation, repeated fetches, revocation, admin authorization, secret-manager failure, transaction-index caching, and tenant access-ID integration.

Important APIs and types: `S3GetSecretRequest`, `S3RevokeSecretRequest`, `S3GetSecretResponse`, `S3RevokeSecretResponse`, `S3SecretLockedManager`, `S3SecretManagerImpl`, `S3SecretCache`, `S3SecretValue`, `S3Secret`, `OMMultiTenantManager`, `OMTenantCreateRequest`, `OMTenantAssignUserAccessIdRequest`, `OmDBAccessIdInfo`, `AuthorizerLockImpl`, Kerberos `UserGroupInformation`, and Hadoop RPC `Server.Call`.

Control flow: setup configures Kerberos name rules, creates Alice and Carol UGIs, installs Alice as current RPC user, builds a real metadata manager and real locked S3 secret manager, and mocks multi-tenant manager behavior. Helper `processSuccessSecretRequest` wraps original and pre-executed requests, calls `validateAndUpdateCache`, and checks response content depending on whether a new secret is expected. `processFailedSecretRequest` verifies unauthorized pre-execute rejects with `USER_MISMATCH`.

State and persistence behavior: successful first fetch creates a secret in metadata/cache and returns it; repeated fetch for an existing secret returns null `S3SecretValue` to avoid overwriting existing DB entry. Cache entries record transaction log index. Revocation removes the old secret; a later get creates a different secret. Tenant test creates tenant metadata, assigns Bob access ID, creates a secret during assignment, then verifies `GetS3Secret` for that access ID returns success but no replacement secret value.

Dependencies and integration points: exercises S3 admin and Ozone admin distinctions, current RPC user, Kerberos short names, tenant manager access-ID mapping, layout-version manager for tenant feature checks, and secret manager locking. It also tests injected `IOException` from `storeSecret`.

Risks covered: privilege escalation for another user's secret, Ozone admin incorrectly acting as S3 admin, stale secret reuse after revocation, cache transaction index loss, overwriting tenant-assigned secrets, and unhandled secret-manager failures.

Test signals: instance checks for response classes, `OMResponse.success`, returned or null `S3SecretValue`, equality of Kerberos IDs, non-null generated AWS secret, cache transaction indexes, changed secret after revoke, `USER_MISMATCH` exceptions, and thrown exception on failing secret manager.
