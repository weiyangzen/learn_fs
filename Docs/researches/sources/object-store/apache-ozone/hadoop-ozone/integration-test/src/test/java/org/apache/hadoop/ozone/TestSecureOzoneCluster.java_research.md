# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestSecureOzoneCluster.java

## Purpose
`TestSecureOzoneCluster` is a broad secure-mode integration test for Ozone SCM and OM. It validates Kerberos startup, SCM security protocol authentication, admin authorization, OM secure initialization, delegation-token renewal, S3 secret authorization, OM certificate initialization and rotation, cross-secret-key token renewal, and gRPC TLS certificate renewal behavior.

## Important APIs, Types, and Functions
- Security setup uses `MiniKdc`, `UserGroupInformation`, Kerberos principals/keytabs, `HADOOP_SECURITY_AUTHENTICATION`, and Ozone/SCM/OM Kerberos config keys.
- SCM setup uses `StorageContainerManager.scmInit`, `HddsTestUtils.getScmSimple`, `ScmInfo`, `SCMSecurityProtocolClientSideTranslatorPB`, `HAUtils.getScmContainerClient`, and `StorageContainerLocationProtocol`.
- OM setup uses `OMStorage`, `OzoneManager.createOm`, `OzoneManager.omInit`, `OzoneManager.setTestSecureOmFlag`, `OzoneManagerProtocolClientSideTranslatorPB`, `OmTransportFactory`, and `ScmTopologyClient`.
- Certificate paths use `SecurityConfig`, `OMCertificateClient`, `DefaultCertificateClient`, `CertificateCodec`, `CertificateClientTestImpl`, `SelfSignedCertificate`, `DefaultApprover`, `CertificateSignRequest`, and `SCMGetCertResponseProto`.
- Token and secret paths use `Token<OzoneTokenIdentifier>`, `ManagedSecretKey`, `SecretKeyTestClient`, `S3SecretValue`, `DELEGATION_TOKEN_MAX_LIFETIME_KEY`, and `HDDS_SECRET_KEY_EXPIRY_DURATION`.
- Helper methods `setSecureConfig`, `createCredentialsInKDC`, `initSCM`, `setupOm`, `initializeOmStorage`, `validateCertificate`, `generateSelfSignedX509Cert`, and `signX509Cert` define the reusable secure test environment.

## Control Flow
`init` allocates random ports, enables security and Kerberos, sets certificate-renewal/grace timers and delegation-token lifetime, creates MiniKdc principals, generates an OM key pair, and builds OM details. `stop` shuts down KDC, SCM, OM, and OM client. SCM tests initialize SCM storage and assert secure startup, security-protocol success for a keytab-authenticated user, failure for token-only users, and admin-command denial for non-admin or unauthenticated users. Kerberos failure tests deliberately clear or corrupt principal/authentication settings and reuse `testCommonKerberosFailures`.

OM tests start secure SCM, initialize OM storage, and then validate successful login/startup, secure client volume creation, no retry on access-control authentication failure, and secret-manager lifetime validation. Delegation-token tests obtain a token over Kerberos, renew it, then assert expiration, renewer mismatch, and tampered-token failures. S3 secret tests cover get, duplicate get, revoke, set after revoke, admin access to other users, and non-admin `USER_MISMATCH` failures.

Certificate tests cover multiple phases: reinitializing a previously insecure OM into secure mode; first secure OM certificate acquisition from SCM and trust-chain persistence; periodic certificate rotation with mocked SCM responses; recoverable rotation failure where an invalid response leaves the old cert in place until a valid response arrives; unrecoverable rollback failure where OM termination is expected; and gRPC TLS renewal where old and new clients continue to connect after OM certificate renewal and old certificate expiry. The cross-secret-key token test injects `SecretKeyTestClient`, rotates the current secret key, obtains a new token with the new key id, and proves an older token remains renewable while the old key is still valid.

## State and Persistence Behavior
The suite writes SCM and OM metadata under temp directories through `SCMStorageConfig` and `OMStorage`, including cluster IDs, SCM IDs, OM IDs, certificate serial IDs, keys, and certificates. Certificate rotation writes certificates through `CertificateCodec` and checks serial-number changes in the active certificate client. Token state lives in OM's delegation-token/secret-key machinery, while `SecretKeyTestClient` keeps generated keys in memory by UUID. Kerberos state is externalized in MiniKdc keytab files. Several tests intentionally share or override principals because SCM and OM run in the same JVM and Hadoop UGI state can otherwise conflict.

## Dependencies and Integration Points
This file ties together MiniKdc, Hadoop RPC/SASL, SCM security service, OM RPC/gRPC transports, Ozone Manager storage, SCM certificate authority behavior, token renewal logic, S3 secret APIs, certificate file layout, and process-exit paths. It also uses log capture from `OzoneManager`, `OMCertificateClient`, `Client`, and `ExitUtil` as observable integration signals.

## Risks and Edge Cases
Timing-sensitive tests depend on sleeps, certificate lifetimes, renewal grace periods, and `GenericTestUtils.waitFor`; slow hosts can make rotation and expiry checks flaky. `testGetSetRevokeS3Secret` is marked flaky for HDDS-9349 and `testOMGrpcServerCertificateRenew` is marked unhealthy for HDDS-8764. Same-JVM UGI behavior is a known risk; `initSCM` rewrites the SCM Kerberos principal to the OM principal to let OM contact SCM. Several tests assert specific exception messages and log strings, making them sensitive to message changes even if behavior remains correct. Exit-path tests disable system exits and inspect logs, so cleanup and global static state such as `OzoneManager.setUgi` and `GrpcOmTransport.setCaCerts` must be restored.

## Test Signals
Strong signals include trust-chain sizes, successful CA certificate retrieval only with Kerberos, exact admin/authentication failures, OM login log output, single no-retry access-control log occurrence, correct token kind/service/secret-key id, `TOKEN_EXPIRED` and `USER_MISMATCH` result codes, S3 secret changes after revoke, certificate subject/issuer/validity checks, certificate serial changes after renewal, old-token renewal across secret-key rotation, and gRPC client success before and after OM certificate renewal.
