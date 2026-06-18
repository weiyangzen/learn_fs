# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenSecretManager.java

## Purpose
`ContainerTokenSecretManager` creates and signs short-lived container tokens using the current symmetric secret key.

## Important APIs, Types, And Functions
It extends `ShortLivedTokenSecretManager<ContainerTokenIdentifier>` and implements `ContainerTokenGenerator`. The constructor takes token lifetime and `SecretKeySignerClient`. `createIdentifier()` builds a `ContainerTokenIdentifier`. `generateEncodedToken()` uses the current Hadoop user and URL-encodes the generated token. `generateToken(String, ContainerID)` signs an identifier through the base class.

## Control Flow
Token generation derives expiry via `getTokenExpiryTime()`, creates an identifier, then delegates signing to the inherited `generateToken(identifier)`. Current-user lookup and token encoding IO failures are wrapped in `UncheckedIOException`.

## State, Persistence, And Dependencies
State is inherited token lifetime and signer client. No direct persistence. Dependencies include Hadoop UGI, container IDs, Hadoop tokens, and symmetric signer clients.

## Integration Points
SCM uses this manager to issue container tokens through `StorageContainerLocationProtocol.getContainerToken()` and other token generator call sites. Datanodes verify resulting identifiers with symmetric key verifiers.

## Risks
Current-user resolution can fail in unusual security contexts. The generated identifier constructor does not set secret-key id directly; correctness depends on the base secret manager assigning it during signing.

## Test Signals
Tests should cover explicit-user and current-user generation, encoded token round trip, unchecked IO wrapping, expiry calculation, and signature verification with the current managed secret key.
