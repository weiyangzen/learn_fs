<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSecretManager.java

Purpose: OM delegation-token secret manager. It creates, verifies, renews, cancels, loads, and expires Ozone delegation tokens, while also validating S3 authentication pseudo-tokens through S3 secrets.

Important APIs/types/functions: Extends `OzoneSecretManager<OzoneTokenIdentifier>`. Builder configures token lifetimes, service, certificate client, secret-key client, S3 secret manager, OM service ID, and OM instance. `createToken` signs identifiers with SCM managed secret keys when the layout feature allows it, otherwise with OM certificate private key. `renewToken`, `cancelToken`, `retrievePassword`, `validateToken`, `verifySignature`, `validateS3AuthInfo`, `loadTokenSecretState`, `addPersistedDelegationToken`, `start`, `stop`, and `removeExpiredToken` form the main lifecycle.

Control flow: Construction loads persisted token renew dates from `OzoneSecretStore` into `currentTokens`. Token creation stamps issue/max dates, sequence number, master key ID, OM service ID, and signing metadata. `retrievePassword` first requires the OM to be leader/ready, then either validates S3 signature or checks token cache expiry and signature. Renewal enforces max date and exact renewer. Cancel enforces owner/renewer authorization but leaves actual removal to higher-level OM request flow. A daemon periodically removes expired tokens from memory and the OM DB.

State and persistence behavior: Maintains `currentTokens` as a `ConcurrentHashMap` of identifiers to renew date/password/tracking info. `OzoneSecretStore` persists renew dates in the delegation token table. Sequence number state is inherited from the base manager. Expiration cleanup mutates both cache and persisted table under `noInterruptsLock`.

Dependencies and integration points: Integrates OM leadership checks, OM layout features, SCM symmetric secret keys, OM X509 certificate client, S3 secret manager, `OzoneSecretStore`, Hadoop `Token`, and Kerberos-name short-name authorization. It is called by `S3SecurityUtil` and normal token-authentication paths.

Risks: Followers reject all token password retrieval to avoid stale token acceptance, which affects failover/read behavior. During upgrade, RSA-signed and symmetric-key-signed tokens coexist; missing secret keys can invalidate unexpired tokens and expired persisted tokens are opportunistically deleted. Signature verification logs sensitive identifiers. `cancelToken` only validates and returns the ID; callers must persist removal. The remover exits the JVM on unexpected exceptions.

Test signals: Strong tests should cover symmetric and RSA signing, persisted-token reload, missing secret key handling, expiration cleanup, renewal authorization, cancel authorization, leader-not-ready wrapping, S3 owner/access-id mismatch, invalid AWS signatures, and upgrade transition token compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSecretManager.java -->
