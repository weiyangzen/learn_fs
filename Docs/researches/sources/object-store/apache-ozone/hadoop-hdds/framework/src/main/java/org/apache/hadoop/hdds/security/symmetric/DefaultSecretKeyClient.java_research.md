# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyClient.java

## Purpose
`DefaultSecretKeyClient` composes separate signer and verifier clients into the combined `SecretKeyClient` interface for components that need both current-key signing and historical-key verification.

## Important APIs, Types, And Functions
It delegates `getCurrentSecretKey()`, `start()`, and `stop()` to a `SecretKeySignerClient`, and delegates `getSecretKey(UUID)` to a `SecretKeyVerifierClient`. Static `create()` wires `DefaultSecretKeySignerClient` and `DefaultSecretKeyVerifierClient` around a `SecretKeyProtocol`.

## Control Flow
There is no independent logic beyond delegation. `start()` only starts the signer side because the verifier cache initializes in its constructor.

## State, Persistence, And Dependencies
State is two delegate references. There is no direct persistence. Dependencies include `SecretKeyProtocol`, configuration, and SCM security exceptions.

## Integration Points
OM/SCM/datanode components can use this combined client when they both issue and verify short-lived symmetric-key tokens.

## Risks
The local variable in `create()` is named `singerClient`, a typo with no behavioral impact. Verifier resources are not stopped because it has no lifecycle method.

## Test Signals
Tests should verify delegation, factory wiring, signer startup/stop behavior, and verifier exception propagation.
