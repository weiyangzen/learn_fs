# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestBlockTokenVerifier.java

## Purpose

This class specializes the abstract token-verifier test matrix for `BlockTokenVerifier`.

## Important APIs, Types, And Functions

It overrides `tokenEnabledConfigKey`, `newTestSubject`, `unverifiedRequest`, `verifiedRequest`, and `newTokenId`. It uses `HDDS_BLOCK_TOKEN_ENABLED`, `BlockTokenVerifier`, `OzoneBlockTokenIdentifier`, `MockPipeline`, close-container requests, write-chunk requests, `BlockID`, and all block access modes.

## Control Flow

The inherited tests build enabled/disabled security config, create verified and unverified container commands, create a signed token through the mock secret manager, and exercise verification paths. For block tokens, close-container is treated as unverified, while write-chunk requires a block token.

## State And Persistence

State is in-memory token identifiers with a fixed test secret key UUID and future expiry. No persistence is used.

## Dependencies And Integration Points

It integrates block-token verification with container command request classification and shared short-lived token verification behavior.

## Risks

Coverage depends on inherited tests; this class only defines block-specific fixtures. The verified request uses a fixed block ID matching the token service.

## Test Signals

Signals include inherited checks for disabled verification, skipped unrelated commands, expired key rejection, missing key rejection, invalid signature rejection, expired token rejection, and valid block-token acceptance.
