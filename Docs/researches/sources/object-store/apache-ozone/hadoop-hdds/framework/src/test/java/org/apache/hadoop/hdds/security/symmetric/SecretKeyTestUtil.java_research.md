# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyTestUtil.java

## Purpose

This test utility generates `ManagedSecretKey` instances for symmetric-key tests.

## Important APIs, Types, And Functions

`generateKey(String, Instant, Duration)` creates a JCA `KeyGenerator` for the requested algorithm, generates a `SecretKey`, assigns a random UUID, and builds a `ManagedSecretKey` with creation and expiry times. `generateHmac` specializes this to `HmacSHA256`.

## Control Flow

Callers request a key for a creation time and validity duration. The utility computes expiry as `creationTime.plus(validDuration)`.

## State And Persistence

The utility is stateless. Generated keys are in-memory only and are not stored.

## Dependencies And Integration Points

It integrates with JCA `KeyGenerator`, `SecretKey`, UUIDs, and the production `ManagedSecretKey` type.

## Risks

Algorithms must be available in the active JCA provider. Random IDs and key material mean tests should not compare generated keys except where explicitly captured.

## Test Signals

Signals are indirect: generated keys can sign/verify, expire at expected times, and match requested algorithms.
