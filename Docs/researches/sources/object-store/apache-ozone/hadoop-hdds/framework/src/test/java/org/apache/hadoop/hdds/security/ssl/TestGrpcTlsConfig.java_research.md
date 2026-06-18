# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestGrpcTlsConfig.java

## Purpose

This class tests TLS protocol and cipher-suite enforcement for Ozone gRPC endpoints using Netty gRPC with mutual TLS.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl`, `NettyServerBuilder`, `NettyChannelBuilder`, `GrpcSslContexts`, `SslContextBuilder`, `SslProvider.JDK`, `ClientAuth.REQUIRE`, `SupportedCipherSuiteFilter`, and the generated `XceiverClientProtocolServiceGrpc` stub. Helpers are `setupServer`, `setupClient`, `sendRequest`, and `shutdown`.

## Control Flow

Each test starts an ephemeral TLS server, builds a TLS client with selected protocols/ciphers, sends a create-container request through a streaming RPC, and asserts success or `ExecutionException`. The fake service replies with `ContainerProtos.Result.SUCCESS`.

## State And Persistence

State is runtime TLS context state, certificate/key material from `CertificateClientTestImpl`, gRPC server/channel objects, and a `CompletableFuture` for response capture. Nothing persists to disk.

## Dependencies And Integration Points

The suite integrates HDDS security config, generated datanode container protobuf/gRPC APIs, pipeline/test request builders, Ratis-shaded gRPC/Netty, and certificate managers.

## Risks

TLS 1.3 and cipher availability depends on JDK/provider support. Unsupported cipher filtering is explicitly tested server-side. The test uses localhost networking and can be sensitive to async failure timing.

## Test Signals

Signals include TLS 1.3 success, TLS 1.2 rejection against TLS 1.3-only server, matching cipher success, mismatched cipher failure, default TLS config success, and successful filtering of a fake configured server cipher.
