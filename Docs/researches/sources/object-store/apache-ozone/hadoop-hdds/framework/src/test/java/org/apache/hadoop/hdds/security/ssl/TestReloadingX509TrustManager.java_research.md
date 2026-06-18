# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509TrustManager.java

## Purpose

This test verifies that `ReloadingX509TrustManager` expands accepted issuers after root CA renewal and reloads once.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl.getTrustManager`, `getRootCACertificate`, `renewRootCA`, `renewKey`, `ReloadingX509TrustManager.getAcceptedIssuers`, and log capture.

## Control Flow

The test obtains a trust manager, asserts only the initial root CA is accepted, renews root CA and leaf key, then asserts both old and new root certificates are accepted and one reload was logged.

## State And Persistence

State is the in-memory root certificate set, trust manager keystore, and captured logs. Nothing persists to disk.

## Dependencies And Integration Points

It validates certificate notification integration between test certificate client and SSL trust manager.

## Risks

The test assumes root CA rotation appends trust rather than replacing it. Log text and count are brittle but intentional reload signals.

## Test Signals

Signals are accepted-issuer set before and after rotation, root certificate inequality, reload log presence, and exactly one reload event.
