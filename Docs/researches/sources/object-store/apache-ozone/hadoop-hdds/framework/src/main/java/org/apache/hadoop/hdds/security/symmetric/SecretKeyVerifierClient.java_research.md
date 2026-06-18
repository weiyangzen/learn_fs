# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyVerifierClient.java

## Purpose
`SecretKeyVerifierClient` defines the verifier-side API for resolving the symmetric key identified by a token.

## Important APIs, Types, And Functions
`getSecretKey(UUID)` returns a nullable `ManagedSecretKey` and may throw `SCMSecurityException`.

## Control Flow
There is no implementation flow in this interface.

## State, Persistence, And Dependencies
The interface has no state. Dependencies are UUIDs, nullable annotation, managed keys, and SCM security exceptions.

## Integration Points
Short-lived token verifiers call this API using the secret-key id embedded in token identifiers. `DefaultSecretKeyVerifierClient` implements remote cached lookup; `SecretKeyManager` implements local SCM lookup.

## Risks
Callers must handle null results as missing/unknown keys and distinguish them from thrown security/IO failures.

## Test Signals
Implementation tests should cover successful key resolution, missing key null returns, and exception propagation.
