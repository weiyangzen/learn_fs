# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMetadataReader.java

Purpose: Tests `OmMetadataReader.getClientAddress`, which chooses the client IP address for audit/security paths across gRPC and Hadoop RPC calls.

Important APIs and types: `OmMetadataReader`, static `io.grpc.Context.key("CLIENT_IP_ADDRESS")`, `Context.Key.get`, and static `org.apache.hadoop.ipc_.Server.getRemoteAddress`.

Control flow: the test uses Mockito static mocks for gRPC context and Hadoop RPC server state. It first returns a gRPC client IP, then a missing gRPC value, then a Hadoop RPC remote address, asserting the method prioritizes gRPC and falls back correctly.

State and persistence: no persistence. State is thread/context-local behavior simulated by static mocks.

Dependencies and integration points: integrates with OM request handling over gRPC and Hadoop RPC. The output is likely consumed by ACL/audit code that records request origin.

Risks and edge cases: static mocking can hide context key changes; returning empty string for missing gRPC address is an explicit contract. Fallback order matters if both transports expose values.

Test signals: expected gRPC IP, empty string for absent context value, and expected Hadoop RPC address after gRPC no longer yields one.
