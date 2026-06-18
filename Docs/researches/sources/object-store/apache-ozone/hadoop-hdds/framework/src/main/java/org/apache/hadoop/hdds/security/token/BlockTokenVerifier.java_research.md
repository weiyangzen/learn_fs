# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenVerifier.java

## Purpose
`BlockTokenVerifier` verifies short-lived block tokens for datanode container commands, including service matching and access-mode authorization.

## Important APIs, Types, And Functions
It extends `ShortLivedTokenVerifier<OzoneBlockTokenIdentifier>`. Static `getTokenService()` converts `BlockID` or `ContainerBlockID` to the token service string. Overrides include `isTokenRequired()`, `createTokenIdentifier()`, `getService()`, and `verify()`.

## Control Flow
Token requirement is true only when block tokens are enabled and `HddsUtils.requireBlockToken(cmdType)` says the command requires one. `getService()` extracts the block id from the command and requires it to be non-null. `verify()` maps read-only commands to `READ`, delete block/chunk to `DELETE`, and all others to `WRITE`, then checks the token identifier contains that access mode.

## State, Persistence, And Dependencies
State is inherited from the short-lived verifier: security config and secret-key verifier client. No persistence. Dependencies include datanode command protobufs, block IDs, HDDS token utility methods, access-mode protobufs, and symmetric key verification.

## Integration Points
Datanode command handling uses this verifier to authenticate block operations. It composes with other verifiers through `CompositeTokenVerifier`.

## Risks
Access-mode classification depends on `HddsUtils.isReadOnly()` and explicit delete command checks; new command types must be classified correctly. Missing block IDs trigger `NullPointerException` via `Objects.requireNonNull`.

## Test Signals
Tests should cover token-required command matrix, READ/WRITE/DELETE permission checks, service string matching, missing block id behavior, disabled block-token mode, and invalid signature/expired token paths inherited from the base verifier.
