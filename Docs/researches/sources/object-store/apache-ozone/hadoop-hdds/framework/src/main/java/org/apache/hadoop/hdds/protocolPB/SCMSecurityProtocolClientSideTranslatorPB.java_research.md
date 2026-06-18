# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SCMSecurityProtocolClientSideTranslatorPB.java

## Purpose

This client translator adapts `SCMSecurityProtocol` to the wrapper-based `SCMSecurityProtocolPB` RPC service with failover/retry support.

## Important APIs, Types, and Functions

The constructor wraps a `SCMSecurityProtocolFailoverProxyProvider` in a `RetryProxy`. `submitRequest(Type, Consumer<Builder>)` builds a traced wrapper request. Public methods implement datanode/OM/SCM/generic certificate issuance, certificate lookup/listing, CA/root CA retrieval, all-root-CA retrieval, and expired-certificate removal.

## Control Flow

Each protocol method builds the specific nested request, sets the wrapper command type and trace ID, invokes `rpcProxy.submitRequest`, calls `handleError`, and extracts the response field. Non-OK status maps by ordinal to `SCMSecurityException.ErrorCode`; protobuf service errors become remote IOExceptions.

## State and Persistence Behavior

State is the retrying PB proxy. Certificate persistence is server-side in SCM metadata.

## Dependencies and Integration Points

It integrates SCM security failover providers, tracing, generated security protobufs, and `SCMSecurityException`.

## Risks and Test Signals

Ordinal status-to-error mapping requires enum order compatibility. Some methods return only leaf certificate strings while chain helpers expose full response protos. Tests should cover every `Type`, trace ID propagation, non-OK status mapping, failover proxy close, and certificate-chain fields.
