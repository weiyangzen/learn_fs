# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenIdentifier.java

## Purpose

This class tests `OzoneBlockTokenIdentifier` signing, invalid-signature rejection, Hadoop token URL encoding/decoding, protobuf field reading, equality, and max-length preservation.

## Important APIs, Types, And Functions

It uses `OzoneBlockTokenIdentifier`, `ManagedSecretKey`, `SecretKeyTestUtil.generateHmac`, Hadoop `Token`, `Text`, `readFields`, `getBytes`, `getKind`, `getMaxLength`, and access-mode enums.

## Control Flow

Setup creates a future expiry time and HMAC key. `testSignToken()` signs a token identifier and verifies valid and random signatures. `testTokenSerialization()` embeds identifier/password in a Hadoop token, URL-encodes/decodes it, reads a new identifier from the decoded bytes, and verifies equality and signature.

## State And Persistence

State is in-memory token bytes, signatures, and encoded string. No disk persistence is used, but serialization compatibility is validated.

## Dependencies And Integration Points

The test integrates HDDS block token identifiers with Hadoop security token transport encoding and symmetric signature verification.

## Risks

The expiry setup uses `Time.monotonicNow()` while other tests use wall-clock `Instant`; token semantics must remain compatible with the identifier implementation. Random invalid signatures should never verify.

## Test Signals

Signals include true verification for signed bytes, false verification for random bytes, decoded identifier equality, max-length equality, and valid decoded token password verification.
