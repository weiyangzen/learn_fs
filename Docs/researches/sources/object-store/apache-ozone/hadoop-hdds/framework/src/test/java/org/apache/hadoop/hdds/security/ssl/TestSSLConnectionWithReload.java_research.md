# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestSSLConnectionWithReload.java

## Purpose

This integration-style test verifies that a gRPC mutual-TLS connection continues working after the certificate client renews its key and reload-capable managers update.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl`, `SecurityConfig.getGrpcSslProvider`, Netty gRPC builders, `GrpcSslContexts`, `ReloadingX509KeyManager`/trust manager through the certificate client, and generated container RPC stubs. Helpers are `setupServer`, `setupClient`, `sendRequest`, and the nested fake `GrpcService`.

## Control Flow

The test starts a TLS server and client, sends a create-container request successfully, calls `caClient.renewKey()`, sleeps for `RELOAD_INTERVAL`, and sends another request over the same channel expecting success.

## State And Persistence

State is in-memory certificate/key material, SSL contexts, gRPC connection state, and futures. `KeyStoresFactory` variables are declared but remain null in this implementation.

## Dependencies And Integration Points

It integrates HDDS certificate reload notifications, Netty TLS, gRPC streaming RPCs, and container command protobufs.

## Risks

The fixed sleep is timing-sensitive and may be slow or flaky. Existing TLS sessions may not fully renegotiate depending on provider behavior, so the test primarily guards practical request continuity.

## Test Signals

Signals are `SUCCESS` responses before and after key renewal, and clean shutdown of channel/server.
