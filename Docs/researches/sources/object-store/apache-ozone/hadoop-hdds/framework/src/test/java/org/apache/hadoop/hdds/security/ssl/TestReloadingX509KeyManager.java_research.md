# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509KeyManager.java

## Purpose

This test verifies that `ReloadingX509KeyManager` updates its private key when the certificate client renews key material and emits exactly one reload log entry.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl.getKeyManager`, `getPrivateKey`, `renewRootCA`, `renewKey`, `ReloadingX509KeyManager.getPrivateKey`, and `LogCapturer`.

## Control Flow

The test obtains the initial key manager and private key, verifies lookup by component alias, renews the root CA and leaf key, verifies a different private key is returned from the same key manager, and inspects reload logs.

## State And Persistence

State lives in the test certificate client, key manager keystore contents, and captured logs. No disk persistence is used.

## Dependencies And Integration Points

It integrates certificate notification callbacks from `CertificateClientTestImpl` with the SSL key manager reload path.

## Risks

The alias convention `componentName + "_key"` is a coupling point. Log-count assertions are sensitive to logging changes and shared static certificate client setup.

## Test Signals

Signals are initial key equality, renewed key inequality, updated manager key equality, presence of reload log text, and exactly one reload.
