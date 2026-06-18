# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyClient.java

## Purpose
`SecretKeyClient` is the combined interface for components that both sign with the current secret key and verify using historical keys.

## Important APIs, Types, And Functions
It extends `SecretKeySignerClient` and `SecretKeyVerifierClient` without adding methods.

## Control Flow
There is no control flow in this interface.

## State, Persistence, And Dependencies
The interface has no state. Implementations may cache keys or manage background refresh and persistence.

## Integration Points
`DefaultSecretKeyClient` composes remote signer/verifier clients, while `SecretKeyManager` implements this interface directly for SCM's local key authority.

## Risks
Consumers should be aware that signer and verifier lifecycle semantics differ; `start()` and `stop()` come from signer side only.

## Test Signals
Implementation tests should verify both inherited contracts through the combined type.
