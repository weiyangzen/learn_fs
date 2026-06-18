<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/S3SecurityUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/S3SecurityUtil.java

Purpose: Utility for constructing and validating OM-side S3 authentication information embedded in `OMRequest`.

Important APIs/types/functions: `validateS3Credential(OMRequest, OzoneManager)` checks security enablement, constructs an `OzoneTokenIdentifier` of type `S3AUTHINFO`, and delegates signature verification to `ozoneManager.getDelegationTokenMgr().retrievePassword`. `constructS3Token` copies string-to-sign, signature, AWS access ID, and owner into the token identifier.

Control flow: If security is disabled, validation is a no-op. If enabled, invalid signatures become `OMException` with `INVALID_TOKEN`. Leader/not-ready errors wrapped as `SecretManager.InvalidToken` causes are rethrown as `ServiceException` to trigger normal client failover behavior.

State and persistence behavior: No persistence. It builds a transient token identifier and relies on delegation token/S3 secret managers for secret lookup and signature validation.

Dependencies and integration points: Called by `OzoneManagerProtocolServerSideTranslatorPB` before S3-authenticated requests proceed. Integrates generated S3 auth protobuf, OM leader status, `OzoneDelegationTokenSecretManager`, and AWS V4 validation indirectly.

Risks: Error logging includes the constructed S3 token on signature failures. Cause checks compare exact exception classes rather than `instanceof`. Missing or malformed S3 auth fields are not locally validated here and depend on deeper validation.

Test signals: Tests should exercise security-disabled no-op, valid signature pass-through, invalid signature status/message, leader-not-ready conversion to `ServiceException`, and token construction fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/S3SecurityUtil.java -->
