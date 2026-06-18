# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3SecretRequestHelper.java

Purpose: tests `S3SecretRequestHelper.getOrCreateUgi`, the helper that resolves a `UserGroupInformation` for S3 secret requests from either the current RPC call or an access ID string.

Important APIs and types: `S3SecretRequestHelper`, `Server.getCurCall`, `ExternalCall`, `UserGroupInformation`, `KerberosName`, and SASL `KERBEROS` auth method. A private `StubCall` extends `ExternalCall<String>` and returns a predefined UGI.

Control flow: setup installs Kerberos name rules and creates expected/test remote users for `access/server@EXAMPLE.COM` with Kerberos auth. One test sets current RPC call to `StubCall` and checks helper returns equivalent UGI. Another leaves call absent and checks helper creates UGI from access ID. A third passes null and expects null. Teardown clears `Server.getCurCall`.

State and persistence behavior: no OM metadata state. The only mutable global state is the thread-local current RPC call and Kerberos name rules.

Dependencies and integration points: supports S3 secret request authorization paths that need a UGI for tenant access IDs or current callers. Correct auth method preservation matters for downstream admin checks and audit identity.

Risks covered: null access IDs, leaking current RPC call between tests, ignoring current caller when available, and creating UGI with wrong user/auth method.

Test signals: equality of user name and authentication method, and null result for null access ID.
