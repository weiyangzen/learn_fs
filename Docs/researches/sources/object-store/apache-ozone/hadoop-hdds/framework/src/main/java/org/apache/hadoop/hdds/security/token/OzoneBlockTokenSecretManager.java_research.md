# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSecretManager.java

## Purpose

`OzoneBlockTokenSecretManager` issues short-lived Ozone block tokens. It creates `OzoneBlockTokenIdentifier` instances carrying owner, `BlockID`, access modes, expiry time, and maximum allowed length, then signs them with the current managed secret key inherited from `ShortLivedTokenSecretManager`.

## Important APIs, Types, and Functions

The constructor takes token lifetime and `SecretKeySignerClient`. `createIdentifier(String, BlockID, Set<AccessModeProto>, long)` builds the token identifier with `getTokenExpiryTime().toEpochMilli()`. `generateToken(String, BlockID, Set<AccessModeProto>, long)` creates a Hadoop `Token` whose identifier bytes/password/kind/service come from the identifier. `generateToken(BlockID, Set<AccessModeProto>, long)` derives the owner from `UserGroupInformation.getCurrentUser().getShortUserName()`.

## Control Flow

The generation path computes an identifier, logs issuance details when debug is enabled, calls `createPassword` to set the signing key ID and signature, then creates the token with the block service text. The UGI overload only resolves the current user and delegates.

## State and Persistence Behavior

No local token database is maintained. State is embedded in the signed token identifier and depends on the externally managed secret key lifecycle. Token validity persists until the identifier expiry time or signing key expiry.

## Dependencies and Integration Points

It integrates with block access mode protobufs, `BlockID`, Hadoop tokens, UGI, and `SecretKeySignerClient`. Generated tokens are consumed by block token verifiers on container command handling paths.

## Risks and Edge Cases

A null current UGI produces a null owner. Access modes and max length are trusted inputs at creation time and need caller-side correctness. Log guard uses debug check but logs at info level, which can surprise operators if debug is enabled.

## Test Signals

Tests should assert service equals the block ID, secret key ID is populated, password verifies with the signer key, expiry follows configured lifetime, owner selection from UGI works, and max-length/access-mode fields round-trip through token serialization.
