# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509KeyManager.java

## Purpose
`ReloadingX509KeyManager` is an `X509ExtendedKeyManager` that can rebuild its in-memory key manager when certificate material changes, allowing TLS endpoints to use renewed private keys and certificate chains without reconstructing the whole component.

## Important APIs, Types, And Functions
The constructor takes keystore type, component name, private key, and trust chain, and initializes an atomic delegate. It overrides all client/server alias, chain, and private-key methods. `notifyCertificateRenewed()` reloads from `CertificateClient`. Internal `init()` builds an in-memory `KeyStore`, inserts the key entry under `componentName + "_key"`, initializes `KeyManagerFactory`, and stores current material. `isAlreadyUsing()` compares private key and certificate serials.

## Control Flow
Most methods delegate to `keyManagerRef.get()`. `chooseEngineClientAlias()` includes a fallback to the known alias when the delegate returns null, working around native Netty/tc-native stale accepted-issuer behavior during certificate refresh. Renewal callbacks call `init()` and swap the atomic reference only when material changed.

## State, Persistence, And Dependencies
State includes keystore type, alias, current private key, current trust chain, and `AtomicReference<X509ExtendedKeyManager>`. The keystore is in-memory only with an empty password. Dependencies include Java SSL/security APIs and `CertificateClient` notification.

## Integration Points
`DefaultCertificateClient` and SSL context builders use this manager for dynamically renewed mTLS key material.

## Risks
The fallback alias can select a certificate even when the delegate could not match requested principals. `getCertificateChain()` and `getPrivateKey()` lowercase aliases for JDK behavior. Logging full certificate text may be verbose. `isAlreadyUsing()` compares serial sets, not chain order.

## Test Signals
Tests should cover initial key manager creation, delegate alias methods, null alias fallback, certificate renewal reload/no-op, alias lowercase handling, and SSL handshake behavior after renewal.
