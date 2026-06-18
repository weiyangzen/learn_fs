# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenIdentifier.java

## Purpose
Abstract base class for short-lived HDDS token identifiers, shared by block and similar token types.

## Important APIs and types
Subclasses must implement `getService()` and `readFromByteArray(byte[])`. The base stores owner ID, expiry `Instant`, and secret key UUID. `getUser()` returns a remote user for owner ID, or the token service when owner is empty. `isExpired(Instant)` checks expiry against a supplied time.

## Control flow and state
Fields are mutable through protected setters and public `setSecretKeyId`, allowing deserializers to populate default-constructed tokens. Equality and hash code include owner, expiry, and secret-key ID.

## Dependencies and integration points
It extends Hadoop `TokenIdentifier` and returns Hadoop `UserGroupInformation`. Concrete identifiers integrate with token managers and protocol serialization.

## Risks and test signals
Tests should cover owner-present and owner-empty user derivation, expiry boundary behavior, equality, and deserialization setter paths. Null expiry would cause `isExpired` to throw, so callers should only check fully initialized tokens.
