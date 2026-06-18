## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3SecretRequestHelper.java

Purpose: `S3SecretRequestHelper` provides shared UGI creation and permission checks for S3 secret get, set, and revoke requests.

Important APIs/types/functions: `getOrCreateUgi(String accessId)` returns the thread-local RPC UGI from `ProtobufRpcEngine.Server.getRemoteUser()` or creates a Kerberos remote user for the access ID. `checkAccessIdSecretOpPermission(OzoneManager, UserGroupInformation, String)` enforces tenant-aware or legacy access ID ownership/admin rules.

Control flow: Permission checking first determines whether S3 multi-tenancy is enabled. If enabled and the access ID belongs to a tenant, the caller must be the access ID owner or a tenant/Ozone admin. If enabled but the access ID is not assigned to a tenant, it falls back to legacy checks. Legacy checks require the caller full principal to equal the access ID or the caller to be an S3 admin.

State and persistence behavior: The helper has no mutable persistent state. It only reads tenant manager mappings and OzoneManager admin checks.

Dependencies and integration points: It integrates S3 secret requests with `OMMultiTenantManager`, tenant admin checks, Ozone S3 admin checks, Hadoop `UserGroupInformation`, and RPC remote-user discovery.

Risks and edge cases: `getOrCreateUgi` can return null if no RPC user exists and access ID is empty; callers should validate inputs. Tenant access uses short user name while legacy uses full principal, a deliberate compatibility distinction. The error code is `USER_MISMATCH`, even when `PERMISSION_DENIED` might be semantically closer.

Test signals: Cover tenant owner, tenant admin, Ozone/S3 admin, non-owner rejection, unassigned access ID fallback, full-principal versus short-name behavior, empty access ID handling, and no remote-user paths.
