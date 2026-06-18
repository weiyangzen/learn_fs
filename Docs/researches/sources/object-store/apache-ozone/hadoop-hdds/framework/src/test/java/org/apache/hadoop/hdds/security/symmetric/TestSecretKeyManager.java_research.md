# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestSecretKeyManager.java

## Purpose

This class tests `SecretKeyManager` initialization and rotation behavior over saved key sets of different ages.

## Important APIs, Types, And Functions

It uses `SecretKeyManager.checkAndInitialize`, `checkAndRotate`, `SecretKeyStateImpl`, `SecretKeyStore.load/save`, `ManagedSecretKey`, `SecretKeyTestUtil.generateKey`, and Mockito `ArgumentCaptor`.

## Control Flow

Parameterized load cases simulate first start, restart, and multi-day downtime. The manager either loads retained keys and current key or generates a new key. Rotation cases set initial state, run rotation, then assert whether a new current key was generated, expired keys filtered, and saved state updated.

## State And Persistence

State lives in `SecretKeyStateImpl` and mocked store interactions. Persisted state is represented by lists returned from or captured by the mock `SecretKeyStore`.

## Dependencies And Integration Points

The tests integrate key lifecycle durations, key-store persistence, sorted secret-key state, and HMAC key generation.

## Risks

Time comparisons allow minute-level tolerance; boundary behavior around exact rotation/expiry instants should be reviewed carefully. Parameterized cases mutate expected retained lists by adding the new key, so reused list instances would be risky.

## Test Signals

Signals include new-key generation on empty/fully expired stores, retained key filtering, no rotation for fresh current key, rotation for old current key, persisted rotated key set, correct algorithm, near-now creation time, and expected expiry.
