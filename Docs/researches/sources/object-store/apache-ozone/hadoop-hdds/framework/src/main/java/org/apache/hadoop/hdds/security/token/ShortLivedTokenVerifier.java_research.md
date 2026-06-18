# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenVerifier.java

## Purpose

`ShortLivedTokenVerifier` is the generic verifier for signed, short-lived Ozone tokens. It handles token decoding, signing-key lookup, signature verification, expiration, service matching, and a subclass hook for additional domain checks.

## Important APIs, Types, and Functions

Subclasses implement `isTokenRequired(ContainerProtos.Type)`, `createTokenIdentifier()`, and `getService(ContainerCommandRequestProtoOrBuilder)`. The public `verify(Token<?> token, ContainerCommandRequestProtoOrBuilder cmd)` performs core validation. Protected `verify(T tokenId, cmd)` is a no-op extension hook. Private `verifyTokenPassword` fetches `ManagedSecretKey` by token secret key ID and validates signature state.

## Control Flow

If the command does not require the token type, verification returns early. Otherwise it reads identifier bytes into a new token identifier, verifies the token password against the referenced secret key, rejects expired token identifiers, compares command service string with token service, and finally invokes subclass-specific validation.

## State and Persistence Behavior

It stores immutable `SecurityConfig` and `SecretKeyVerifierClient` references. No decisions are cached; every call consults token bytes, command data, and secret-key client state.

## Dependencies and Integration Points

It integrates Hadoop tokens with Ozone `ContainerProtos`, `SecurityConfig`, `SecretKeyVerifierClient`, `ManagedSecretKey`, and `SCMSecurityException`/`BlockTokenException`. Concrete block and container verifiers plug into `CompositeTokenVerifier`.

## Risks and Edge Cases

Early return depends entirely on subclass command-type classification. Service comparison is string-based. Missing, expired, or unavailable secret keys reject otherwise well-formed tokens. Decode failures hide the original `IOException` detail in a new exception message.

## Test Signals

Exercise non-required command bypass, malformed identifier bytes, missing secret key, expired signing key, invalid signature, expired token, service mismatch, and subclass hook invocation after all common checks pass.
