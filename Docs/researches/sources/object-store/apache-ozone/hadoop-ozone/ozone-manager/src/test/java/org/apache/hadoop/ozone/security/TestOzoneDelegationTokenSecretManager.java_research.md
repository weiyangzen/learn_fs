# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSecretManager.java

## Purpose
`TestOzoneDelegationTokenSecretManager` validates OM delegation token creation, password retrieval, renewal, cancellation, signature verification, expired secret-key handling, leader checks, and S3 auth token validation.

## Important APIs, Types, and Functions
- `OzoneDelegationTokenSecretManager.Builder` wires configuration, token lifetimes, service address, OM, S3 secret manager, certificate client, OM service ID, and secret key client.
- `createToken`, `renewToken`, `cancelToken`, `retrievePassword`, `createIdentifier`, `verifySignature`, and `updateToken` are tested.
- `OzoneTokenIdentifier` carries owner, renewer, real user, token type, secret key ID, certificate serial ID, S3 signature fields, and service ID.
- `SecretKeyTestClient` provides symmetric signing keys; an overridden `OMCertificateClient` provides asymmetric signing and certificate lookup.
- `S3SecretLockedManager` plus `S3SecretStoreMap` provide S3 access secrets.

## Control Flow
Setup creates a temp OM metadata path, security config, certificate client with generated RSA key/cert path, secret key client, mocked OM with metadata manager and layout manager, and an S3 secret manager seeded with test users. Tests then cover: wrapping OM leadership exceptions in `InvalidToken`; creating a token and validating its signature; behavior when secret key IDs cannot be resolved and expired tokens are removed from the delegation token table; renew success with and without secret-manager restart; renew failure for wrong renewer, max lifetime expiry, and renewal interval expiry; empty identifier creation; cancel success and authorization failure; symmetric and asymmetric signature verification; invalid certificate serial failure; and S3AUTHINFO success/failure.

## State and Persistence Behavior
The test uses a real `OmMetadataManagerImpl` backed by the temp metadata path and writes delegation token entries into the delegation token table through `addToTokenStore`. Secret manager restart reloads state from metadata. Expired-token handling deletes stale rows from the delegation token table. Certificate and key material are local in-memory/temporary test artifacts.

## Dependencies and Integration Points
This file integrates security config, certificate codecs, Java cert paths, OM metadata tables, layout version gating, S3 secret managers, leader status checks, Hadoop `Token`, `SecretManager.InvalidToken`, access-control exceptions, Ratis peer IDs, and log capture. It is a broad integration-style unit test for OM token security.

## Risks and Edge Cases
Covered risks include accepting operations on non-leader OMs, losing renewability across restart, allowing unauthorized renew/cancel users, accepting expired tokens, failing to clean expired rows when keys are missing, incorrect symmetric/asymmetric signature validation, and S3 signature validation against absent/invalid secrets. Timing-based tests use sleeps and short lifetimes, which can be sensitive on slow CI.

## Test Signals
This is the strongest security test in the subset. It verifies both cryptographic paths and persisted token table interactions, while also confirming S3 auth delegates to stored S3 secrets and AWS V4 signature logic.
