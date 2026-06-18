# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClientTestImpl.java

## Purpose

This test-only `CertificateClient` implementation creates in-memory root and leaf certificates, exposes reloadable key/trust managers, supports key/root renewal, and provides enough certificate-client behavior for SSL and CA tests.

## Important APIs, Types, And Functions

Key methods include constructors with optional auto-renew, `getPrivateKey`, `getPublicKey`, `getCertificate`, `getTrustChain`, `getCACertificate`, `verifySignature`, `getRootCACertificate`, `getAllRootCaCerts`, `renewRootCA`, `renewKey`, `getKeyManager`, `getTrustManager`, `createClientTrustManager`, `registerNotificationReceiver`, and `close`. Nested `RenewCertTask` triggers root and leaf renewal.

## Control Flow

Construction generates key pairs, creates a self-signed root CA, signs a leaf certificate with `DefaultApprover`, populates certificate maps/sets, and optionally schedules renewal for the configured grace-period start. `renewKey()` generates a new leaf cert, swaps active key/cert, stores it, and notifies registered managers. Key/trust managers are lazily created and registered as notification receivers.

## State And Persistence

State is in-memory: key pairs, current leaf certificate, current/root CA certs, certificate map, notification receivers, and optional scheduled executor. No keys or certs are written to disk.

## Dependencies And Integration Points

It integrates HDDS `SecurityConfig`, key generation, self-signed certificate generation, CSR building/signing, reloadable SSL managers, client trust manager provider callbacks, and certificate notification APIs.

## Risks

It is intentionally incomplete: `getCertPath`, `initWithRecovery`, and root-rotation listener behavior are stubbed. The notification receiver set is a `HashSet` with synchronized writes but unsynchronized iteration during renewal. Auto-renew scheduling depends on wall clock and should be used carefully in tests.

## Test Signals

Signals include valid generated key/cert chain, signature verification, key manager reload after `renewKey`, trust manager issuer expansion after `renewRootCA`, notification delivery with old/new serials, and executor shutdown on close.
