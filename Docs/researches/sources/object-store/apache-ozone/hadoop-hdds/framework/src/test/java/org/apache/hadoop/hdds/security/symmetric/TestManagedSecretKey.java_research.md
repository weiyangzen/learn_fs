# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestManagedSecretKey.java

## Purpose

This class tests `ManagedSecretKey` signing and signature verification for raw bytes, protobuf transfer, and block token identifiers.

## Important APIs, Types, And Functions

It uses `ManagedSecretKey.sign(byte[])`, `sign(TokenIdentifier)`, `isValidSignature`, `toProtobuf`, `fromProtobuf`, `SecretKeyTestUtil.generateHmac`, `OzoneBlockTokenIdentifier`, `BlockID`, and access-mode enums.

## Control Flow

The success test signs random data, verifies with the same key and a protobuf-round-tripped key, then signs a block token and verifies it the same way. The failure test verifies random signatures fail and signatures from one key cannot be verified by another.

## State And Persistence

State is in-memory key material and token identifiers. Protobuf conversion tests serialization fidelity but not disk persistence.

## Dependencies And Integration Points

The class integrates symmetric HMAC keys with HDDS token signing and protobuf exchange.

## Risks

Random test data and key material make failures dependent on crypto implementation behavior but should be deterministic in pass/fail. The test does not cover expired-key checks.

## Test Signals

Signals are successful raw/token verification by same and transferred keys, rejection of random signatures, and rejection by a different key.
