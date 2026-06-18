# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressServerInterceptor.java

Purpose: gRPC server interceptor that reads client hostname/IP metadata and places it into the current gRPC `Context` for downstream service handlers.

Important APIs and types: Implements `ServerInterceptor.interceptCall`, reads `Metadata.Key<String>` constants, uses `Context.current().withValue`, and delegates via `Contexts.interceptCall`.

Control flow: For each RPC, it extracts both metadata headers, creates a derived context containing both values, and continues the call under that context.

State and persistence behavior: No persistent state. The derived context is scoped to the server call.

Dependencies and integration points: Paired with the client interceptor and consumed by server-side authorization/auditing layers that consult `GrpcClientConstants` context keys.

Risks: Null metadata is stored as null context values. Tests should ensure downstream code handles missing client address values. Header names are ASCII and case-sensitive through gRPC metadata conventions.

Test signals: Verify server handlers see the expected context values when headers are present and null values when absent.
