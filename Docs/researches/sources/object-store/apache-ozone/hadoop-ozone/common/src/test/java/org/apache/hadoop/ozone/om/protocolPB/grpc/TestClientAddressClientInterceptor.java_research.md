# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressClientInterceptor.java

Purpose: tests the gRPC client interceptor that adds client IP address and hostname metadata to outgoing requests.

Important APIs/types/functions: exercises `ClientAddressClientInterceptor.interceptCall`, `ClientCall.start`, `GrpcClientConstants.CLIENT_HOSTNAME_METADATA_KEY`, and `CLIENT_IP_ADDRESS_METADATA_KEY`.

Control flow and state: the test statically mocks `Context.key("CLIENT_IP_ADDRESS")` and `Context.key("CLIENT_HOSTNAME")` to return context keys with known values. It intercepts a mocked channel call, starts the returned call with mocked metadata, and verifies both metadata entries are written.

Dependencies and integration points: uses gRPC `ClientInterceptor`, `Context`, `Metadata`, `Channel`, `CallOptions`, `MethodDescriptor`, and Mockito static mocking. It feeds server-side identity/audit paths.

Risks and test signals: catches missing or swapped metadata propagation from client context. It does not cover null context values or downstream server behavior, which is covered by the server interceptor test.
