<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransport.java

## Purpose

`GrpcOmTransport` is the gRPC implementation of `OmTransport`, primarily for S3 gateway to OM communication with HA failover support and optional TLS.

## Important APIs, Types, And Functions

Important methods are static `setCaCerts`, constructor, `start`, `submitRequest`, `unwrapException`, `shouldRetry`, `getDelegationTokenService`, `shutdown`, `close`, `startClient`, and nested `GrpcOmTransportConfig`. It maintains gRPC blocking stubs and managed channels per OM node.

## Control Flow, State, And Persistence

Construction builds a `GrpcOMFailoverProxyProvider`, initializes host state, channel/stub maps, max response size, and retry policy. `submitRequest` injects local client IP/hostname into gRPC context, invokes the current stub, unwraps status exceptions, and uses the retry policy to fail over by updating the current host. `shutdown` closes channels and waits up to a bounded timeout. The transport keeps runtime connection/failover state only.

## Dependencies And Integration Points

It depends on gRPC, Netty TLS, `SecurityConfig`, OM failover proxy provider, retry policies, gRPC client interceptors, OM request/response protobufs, UGI, and Ozone config keys. It integrates with `GrpcOmTransportFactory`, S3 gateway protocol clients, secure service discovery CA material, and OM gRPC service implementations.

## Risks And Test Signals

TLS setup logs errors but may continue with a channel builder; `getDelegationTokenService` returns empty text; exception unwrapping uses reflective class loading and fragile status descriptions. Tests should cover TLS with CA certs, SSL handshake failure mapping, failover on unavailable OM, resource-exhausted/data-loss propagation, client-address metadata, shutdown timeout, concurrent failover, and injected test channels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransport.java -->
