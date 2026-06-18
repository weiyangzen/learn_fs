# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressServerInterceptor.java

Purpose: tests the gRPC server interceptor that reads client address metadata and installs it into gRPC context keys.

Important APIs/types/functions: exercises `ClientAddressServerInterceptor.interceptCall`, `Contexts.interceptCall`, `GrpcClientConstants.CLIENT_HOSTNAME_CTX_KEY`, `CLIENT_IP_ADDRESS_CTX_KEY`, and corresponding metadata keys.

Control flow and state: mocked headers return host and IP values. Static mocking captures the `Context` passed to `Contexts.interceptCall`; after attaching that context, the test asserts the context keys expose the captured host and IP values.

Dependencies and integration points: uses gRPC `ServerInterceptor`, `ServerCall`, `ServerCallHandler`, `Metadata`, `Context`, and Mockito. It completes the client-to-server propagation chain for audit/logging identity details.

Risks and test signals: catches missing context propagation and mismatched metadata/context keys. The test relies on `context.attach()` without detach because it is a short isolated unit test.
