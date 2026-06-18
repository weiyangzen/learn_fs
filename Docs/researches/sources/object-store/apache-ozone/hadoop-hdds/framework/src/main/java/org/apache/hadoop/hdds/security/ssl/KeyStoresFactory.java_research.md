# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/KeyStoresFactory.java

## Purpose
`KeyStoresFactory` defines the abstraction for components that create and expose SSL key managers and trust managers for HDDS clients and servers.

## Important APIs, Types, And Functions
The nested `Mode` enum distinguishes `CLIENT` and `SERVER`. `init(Mode, boolean)` initializes key/trust material and may throw IO or security exceptions. `destroy()` releases resources. `getKeyManagers()` and `getTrustManagers()` return arrays for SSL context construction.

## Control Flow
There is no implementation in this interface. Implementations decide how to load, reload, and destroy keystore/truststore resources.

## State, Persistence, And Dependencies
The interface has no state. Implementations may use disk or in-memory stores. Dependencies are Java SSL manager types and security exception classes.

## Integration Points
TLS-enabled HDDS services use implementations to construct SSL contexts. The reloadable key/trust managers in this package are likely returned through this abstraction.

## Risks
Callers must respect initialization ordering; getters before `init()` may be invalid depending on implementation. `requireClientAuth` is ignored in client mode by contract.

## Test Signals
Implementation tests should verify client/server mode initialization, client-auth behavior, SSLContext compatibility, cleanup, and error propagation.
