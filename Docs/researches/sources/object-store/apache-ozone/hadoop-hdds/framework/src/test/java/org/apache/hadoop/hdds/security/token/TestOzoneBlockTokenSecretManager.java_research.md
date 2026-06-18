# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenSecretManager.java

## Purpose

This class tests block-token generation, identifier creation, service binding to blocks, read/write access enforcement, and expired signing-key rejection.

## Important APIs, Types, And Functions

It uses `OzoneBlockTokenSecretManager`, `BlockTokenVerifier`, `OzoneBlockTokenIdentifier`, `SecretKeySignerClient`, `SecretKeyVerifierClient`, `ManagedSecretKey`, `ContainerTestHelper` request builders, `MockPipeline`, `BlockID`, and access-mode enums.

## Control Flow

Setup creates a pipeline, token-enabled security config, valid secret key, mocked signer/verifier clients, secret manager, and verifier. Tests generate tokens, decode identifiers, verify signatures, build write/put/get/read commands, and assert either successful verification or `BlockTokenException` with expected messages.

## State And Persistence

State is in-memory secret key material, token identifiers, Hadoop tokens, and mocked key-client responses. The temp metadata directory config is set but not central to the tests.

## Dependencies And Integration Points

The suite integrates token signing with datanode command authorization, block service strings, pipeline request builders, and secret-key validity checks.

## Risks

The test uses mocked key clients, so it does not cover network retrieval of secret keys. Error-message assertions are intentionally coupled to verifier diagnostics.

## Test Signals

Signals include correct token service/access modes/key ID/signature, valid put-block use for matching block, rejection for other block, read-only token rejecting write and allowing read, write-only token rejecting read and allowing write, and expired secret-key rejection.
