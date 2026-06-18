# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeyVerifierClient.java

## Purpose
`DefaultSecretKeyVerifierClient` fetches historical symmetric secret keys from SCM on demand and caches them locally for token verification.

## Important APIs, Types, And Functions
The constructor builds a Guava `LoadingCache<UUID, Optional<ManagedSecretKey>>` using expiry and rotation durations from `SecretKeyConfig`. `getSecretKey(UUID)` retrieves a key or null and converts IO/SCM security failures into `SCMSecurityException`.

## Control Flow
Cache sizing estimates how many valid keys can exist as `expiry / rotate + 1`, doubles that to retain recently expired keys, and uses a TTL twice the key expiry duration. Cache misses call `secretKeyProtocol.getSecretKey(id)`.

## State, Persistence, And Dependencies
State is the loading cache. There is no persistence. Dependencies include Guava cache, `SecretKeyProtocol`, duration parsing, and SCM security exception types.

## Integration Points
Datanode/token verifier paths use this client to retrieve the specific key referenced by a token's secret-key UUID.

## Risks
If rotate duration is zero or misconfigured, cache size calculation can divide by zero. Optional-empty results are cached, so a key that appears later may remain absent until TTL expiry. The log says TTL is `expiryDuration` though the actual cache expiry is doubled.

## Test Signals
Tests should cover cache hits/misses, null key caching, exception conversion, cache size/TTL calculation, and behavior with invalid duration configs.
