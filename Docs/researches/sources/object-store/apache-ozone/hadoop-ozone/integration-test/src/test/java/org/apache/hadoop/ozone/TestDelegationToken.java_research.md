# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDelegationToken.java

Purpose: secure Ozone integration test for OM delegation token lifecycle and Hadoop RPC authentication behavior, parameterized by token service using host names or IPs.

Important APIs/types/functions: `init`, `stop`, MiniKdc helpers, `setSecureConfig`, `initSCM`, `testDelegationToken(boolean useIp)`, `generateKeyPair`, and `setupOm`. It uses `StorageContainerManager`, `OzoneManager`, `OzoneManagerProtocolClientSideTranslatorPB`, `OmTransportFactory`, `OzoneTokenIdentifier`, `UserGroupInformation`, `MiniKdc`, SCM/OM storage config, `HASecurityUtils`, and audit log capture.

Control flow: each test creates a secure configuration with random ports, metadata dirs, Kerberos auth, MiniKdc principals/keytabs, SCM security initialization, and an OM key pair. The test starts a simple SCM, captures Hadoop RPC audit logs, configures `SecurityUtil.setTokenServiceUseIp`, creates and starts a secure OM with certificate and topology test clients, closes unrelated SCM clients to force fresh RPC handshakes, then obtains an OM client via Kerberos. It requests a delegation token, renews it, validates token kind/service, closes the Kerberos client, installs the token on a remote UGI using TOKEN auth, creates a new OM client as that UGI, confirms token-authenticated operation reaches OM by expecting `VOLUME_NOT_FOUND` on `deleteVolume`, verifies renewal fails under token auth with `INVALID_AUTH_METHOD`, switches back to Kerberos, cancels the token, waits for client timeout, then confirms further cancellation via the token-authenticated client fails with `TOKEN_ERROR_OTHER`.

State and persistence: Kerberos KDC/keytabs, SCM version/security files, OM version/cert metadata, generated HDDS key pair, UGI login user global state, Hadoop RPC client cache/connection state, OM delegation token cache, and audit logs.

Dependencies and integration points: Hadoop security, MiniKdc, SCM security bootstrap, OM RPC translator, token service construction, UGI auth modes, Hadoop RPC audit logging, and OM exception mapping.

Risks: manipulates global UGI login user and token-service-use-IP flag; failures can leak state into later tests. Sleep-based client timeout is coarse. Log assertions depend on audit message text. The comments highlight Hadoop RPC client caching as a critical subtlety.

Test signals: token issuance/renewal, token kind/service, token-authenticated RPC success, renewal rejection with token auth, cancellation success, post-cancel token failure, and expected OM result codes/log messages.
