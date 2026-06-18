# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestS3GrpcOmTransport.java

Purpose: tests `GrpcOmTransport` request submission, failover retry behavior, per-request failover counts, and non-retry behavior for oversized gRPC metadata/response errors.

Important APIs/types/functions: exercises `GrpcOmTransport.startClient`, `submitRequest`, failover config keys, gRPC in-process server/channel builders, protobuf `ServiceList` requests, and `OMNotLeaderException` error wrapping.

Control flow and state: an in-process gRPC service either returns a fixed successful `OMResponse` or throws a not-leader error depending on `doFailover` and `completeFailover` flags. Tests verify normal submission, one failover followed by success, retry exhaustion with max attempts 0, failover counters reset per request, and `RESOURCE_EXHAUSTED` style max message length failures do not retry.

Dependencies and integration points: uses `GrpcCleanupRule`, `ManagedChannel`, `UserGroupInformation`, `OzoneConfiguration`, and Ratis `RaftPeerId`. This is the direct client transport for gRPC OM calls.

Risks and test signals: catches retry policy regressions, failover counter leakage across requests, and inappropriate retry on response-size/resource errors. The test notes suggested leader ID is not currently used by the client.
