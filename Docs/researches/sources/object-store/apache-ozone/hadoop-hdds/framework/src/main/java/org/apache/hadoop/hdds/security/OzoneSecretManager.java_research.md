# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretManager.java

## Purpose
`OzoneSecretManager` is an abstract asymmetric-token secret manager. It signs token identifiers with the current certificate private key, tracks token/key sequence numbers, starts/stops against a `CertificateClient`, and updates signing material when certificates renew.

## Important APIs, Types, And Functions
It extends Hadoop `SecretManager<T>` and implements `CertificateNotification`. Key methods are `createPassword(byte[], PrivateKey)`, `createPassword(T)`, abstract `renewToken()` and `cancelToken()`, sequence/key incrementors, `start(CertificateClient)`, `stop()`, `notifyCertificateRenewed()`, and accessors for lifetimes, service, current key, cert client, and sequence numbers.

## Control Flow
`start()` asserts the manager is not running, stores the certificate client, creates the initial `OzoneSecretKey` from current key/cert, registers for renewal notifications, and marks running. `notifyCertificateRenewed()` logs serial mismatches and replaces the current key from renewed material. `createPassword(T)` signs identifier bytes with the current private key and returns null if identifier serialization fails.

## State, Persistence, And Dependencies
State includes `SecurityConfig`, token lifetimes, service name, certificate client, running flag, `AtomicReference<OzoneSecretKey>`, current key id, and token sequence number. It persists nothing directly. Dependencies include Java `Signature`, certificate/key APIs, Hadoop tokens, and Ozone security exceptions.

## Integration Points
Concrete delegation/block token managers extend this base. It integrates with `CertificateClient` renewal callbacks and `SecurityConfig.getSignatureAlgo()`.

## Risks
`createPassword(T)` can return null on `IOException`, which may surface later. `getCertSerialId()` assumes a current key exists. Renewal mismatch checks only log and still update. Stop only flips a flag and does not unregister notification receivers.

## Test Signals
Tests should cover start/stop state, initial key creation, signature algorithm failures, sequence increments, renewal callback key replacement, mismatch logging, and concrete renew/cancel implementations.
