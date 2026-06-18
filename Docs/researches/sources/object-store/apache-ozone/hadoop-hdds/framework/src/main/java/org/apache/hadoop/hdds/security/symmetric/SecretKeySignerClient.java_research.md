# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeySignerClient.java

## Purpose
`SecretKeySignerClient` defines the signer-side API for components that need the current symmetric secret key to sign tokens or data.

## Important APIs, Types, And Functions
`getCurrentSecretKey()` is the required method. Default lifecycle hooks `start(ConfigurationSource)`, `stop()`, and `refetchSecretKey()` are no-ops for simple implementations.

## Control Flow
There is no interface control flow. Implementations such as `DefaultSecretKeySignerClient` use `start()` to prefetch and schedule refreshes.

## State, Persistence, And Dependencies
The interface has no state. It depends on `ConfigurationSource` and may throw `IOException` during startup.

## Integration Points
`ContainerTokenSecretManager` and other token signers use this API to access signing keys. `SecretKeyClient` extends it.

## Risks
Default no-op lifecycle methods mean callers cannot assume every implementation prefetches or refreshes keys unless documented.

## Test Signals
Implementation tests should verify initialization requirements, current key availability, refresh behavior, and cleanup.
