# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestGrpcOmTransportConcurrentFailover.java

Purpose: stress-tests `GrpcOmTransport` failover under high concurrency against three in-process mock OM gRPC servers.

Important APIs/types/functions: exercises `GrpcOmTransport.submitRequest`, HA config keys for OM RPC/gRPC addresses, `OzoneManagerServiceGrpc`, `ServerBuilder`, and failover response handling for `OMNotLeaderException` descriptions.

Control flow and state: setup starts three servers on fixed ports, configures OM service ID and nodes, marks `om0` leader, sends warm-up requests, then changes leadership to `om2`. The main test launches 500 threads, each sending 10 `ListVolume` requests through one transport. Mock servers count requests, failures, and successes with atomic counters.

Dependencies and integration points: uses real gRPC servers, Mockito delegation, `UserGroupInformation`, `OzoneConfiguration`, and Java concurrency primitives. It models concurrent clients sharing failover state during OM leadership changes.

Risks and test signals: catches failover synchronization bugs where not all requests eventually reach the new leader. The test expects all concurrent requests to succeed on `om2` and at least one failed request on `om0`; fixed ports and high thread count may be environment-sensitive.
