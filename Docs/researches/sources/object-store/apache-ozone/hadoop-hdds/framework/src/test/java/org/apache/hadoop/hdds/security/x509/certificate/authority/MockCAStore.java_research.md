# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/MockCAStore.java

## Purpose

This class is a no-op `CertificateStore` implementation used by CA tests that need a store dependency without metadata persistence.

## Important APIs, Types, And Functions

It implements `storeValidCertificate`, `checkValidCertID`, `storeValidScmCertificate`, `removeAllExpiredCertificates`, `getCertificateByID`, `listCertificate`, and `reinitialize`. Most methods do nothing; list methods return empty collections and lookup returns null.

## Control Flow

Production CA code can call store methods during tests, but the mock absorbs writes and reports no stored certificates.

## State And Persistence

There is no state and no persistence. Calls do not record certificates or serial IDs.

## Dependencies And Integration Points

It integrates with `DefaultCAServer` tests, `CertificateStore`, `NodeType`, `X509Certificate`, and `SCMMetadataStore`.

## Risks

Because it ignores all writes, it cannot test duplicate serial handling, certificate listing, expiry cleanup, or metadata-store reinitialization. Tests using it validate CA control flow rather than storage semantics.

## Test Signals

Signals are indirect: CA tests proceed without store failures while storage-sensitive behavior remains unverified.
