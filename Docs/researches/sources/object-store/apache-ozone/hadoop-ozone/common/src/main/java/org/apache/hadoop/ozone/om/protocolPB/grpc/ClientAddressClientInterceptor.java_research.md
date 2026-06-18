# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressClientInterceptor.java

Purpose: gRPC client interceptor that propagates caller hostname and IP address from gRPC `Context` into request metadata headers.

Important APIs and types: Implements `ClientInterceptor.interceptCall`, wraps the call in `ForwardingClientCall.SimpleForwardingClientCall`, and writes `GrpcClientConstants` metadata keys during `start`.

Control flow: On call start, it reads `CLIENT_HOSTNAME_CTX_KEY` and `CLIENT_IP_ADDRESS_CTX_KEY`; when values are present it puts them into the corresponding metadata headers before delegating to the original call.

State and persistence behavior: Stateless interceptor. Metadata is per-RPC and not persisted locally.

Dependencies and integration points: Paired with `ClientAddressServerInterceptor`, gRPC channel construction, and any OM/Ranger/audit code that reads client address from server context.

Risks: Local variable names are swapped (`ipAddress` stores hostname and `hostname` stores IP), but the values are written to matching metadata keys. This is confusing and could cause future maintenance mistakes. Missing context values simply omit headers.

Test signals: gRPC interceptor tests should set each context key independently and assert exact metadata header population and absence when null.
