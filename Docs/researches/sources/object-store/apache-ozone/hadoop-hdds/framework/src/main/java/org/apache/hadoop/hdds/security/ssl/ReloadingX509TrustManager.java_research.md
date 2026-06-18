# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/ssl/ReloadingX509TrustManager.java

## Purpose
`ReloadingX509TrustManager` is a reloadable `X509TrustManager` that rebuilds an in-memory trust manager when root CA material changes.

## Important APIs, Types, And Functions
The constructor accepts truststore type and root CA certificates. `checkClientTrusted()`, `checkServerTrusted()`, and `getAcceptedIssuers()` delegate to the current trust manager. `notifyCertificateRenewed()` pulls root CA certificates from `CertificateClient`, falling back to all CA certs when root CA set is empty, then reloads. Internal `init()` constructs a new in-memory `KeyStore`, inserts certs by serial id, and initializes `TrustManagerFactory`.

## Control Flow
Trust checks delegate and log certificate subject principals on failures before rethrowing. Reloading is skipped when the new certificate set has the same serials as the current set. Successful reload swaps `trustManagerRef`.

## State, Persistence, And Dependencies
State includes truststore type, atomic trust manager reference, and the current root CA certificate list. No disk persistence is used. Dependencies include Java SSL/security APIs, certificate notification, and SLF4J.

## Integration Points
Certificate clients register this manager for CA rotation events so long-running TLS endpoints trust renewed or rotated CA chains.

## Risks
If `trustManagerRef` is null and `chain` is empty/null, error construction can access `chain[0]`. Certificate equality is by serial only, not issuer or encoded bytes. Exceptions in renewal are wrapped in runtime exceptions with a fixed reload message.

## Test Signals
Tests should cover initial accepted issuers, client/server trust success and failure logging, reload on changed serials, no-op reload on same serials, empty root set fallback, and null/empty chain behavior.
