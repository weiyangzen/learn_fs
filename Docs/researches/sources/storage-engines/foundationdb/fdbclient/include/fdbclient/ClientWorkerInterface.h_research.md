# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientWorkerInterface.h

Purpose: Declares the subset of worker RPC streams that clients can safely call for management operations: reboot, profiling, failure injection, and optional gRPC address discovery.

Important APIs/types/functions: `ClientWorkerInterface` contains `RequestStream<RebootRequest>`, `RequestStream<ProfilerRequest>`, `RequestStream<SetFailureInjection>`, and optional `grpcAddress`. It exposes identity via the reboot endpoint token and primary address. `initEndpoints()` initializes the reboot endpoint and records the Flow gRPC server address when enabled. `RebootRequest` carries delete/check-data flags and a wait duration. `ProfilerRequest` carries reply promise, profiling `Type` (`GPROF`, `FLOW`, `GPROF_HEAP`), `Action` (`DISABLE`, `ENABLE`, `RUN`), duration, and output file. `SetFailureInjection` supports disk stall/throttle and bit-flip commands.

Control flow: Workers embed this as the first element of their broader worker interface, initialize endpoints, then cluster management clients retrieve `ClientWorkerInterface` values and send management requests to the relevant streams. Requests with replies complete through `ReplyPromise<Void>`.

State and persistence behavior: This is an RPC contract, not durable state. Serialized endpoint fields determine remote routing, and optional gRPC address is discovery metadata. Failure-injection command values are transient and affect worker runtime behavior.

Dependencies and integration points: Depends on Flow gRPC support, `FDBTypes.h`, failure monitoring, status, and commit proxy types. Integrated through `ClusterInterface::GetClientWorkersRequest`, management API reboot/profiler commands, and worker process control handlers.

Risks: Endpoint identity is derived from the reboot stream, so endpoint initialization/order must remain stable. Failure injection is powerful and can corrupt or stall disks in tests, so caller authorization and simulation gating matter. `grpcAddress` is conditional on `FLOW_GRPC_ENABLED`, so clients must handle absence.

Test signals: Worker interface serialization round trips; client-worker discovery; reboot request handling with flags and delay; profiler enable/run/disable; disk stall/throttle and bit-flip failure-injection simulation; builds with and without Flow gRPC.
