# sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.h

## Purpose
`Status.h` declares the cluster-controller status API used to produce full cluster status JSON and fault-tolerance-only status JSON. It also defines the small `ProcessIssues` carrier used to attach issue names to worker network addresses before status rendering.

## Important APIs, Types, and Functions
- `struct ProcessIssues` stores a `NetworkAddress address` and a `Standalone<VectorRef<StringRef>> issues`. The constructor takes both values and stores them directly.
- `clusterGetStatus(...)` returns `AsyncResult<StatusReply>` and accepts the live `ServerDBInfo`, database handle, worker list, process issues, storage-server metadata, client-status map pointer, coordinators, incompatible connection addresses, datacenter/log/storage lag versions, degraded-server gray-failure exclusions, and a deadline timeout.
- `clusterGetFaultToleranceStatus(const std::string& statusString)` returns a `StatusReply` containing a filtered subset of a full status JSON payload.

## Control Flow
The header contains declarations only. Its control-flow significance is in the async return type: callers start `clusterGetStatus` as a Flow actor and eventually receive a `StatusReply`; `clusterGetFaultToleranceStatus` is synchronous over an already available JSON string.

## State and Persistence Behavior
No state is persisted in the header. `ProcessIssues` owns its supplied issue vector and is passed by value in vectors to status collection. `clusterGetStatus` receives a pointer to a mutable client-status map; the implementation prunes stale clients while rendering status.

## Dependencies and Integration Points
The header includes RPC, coordination, worker, master, and cluster interface types from `fdbrpc`, `fdbserver/core`, and `fdbclient`. It is the narrow public declaration surface between the cluster-controller implementation and code that serves cluster status requests.

## Risks and Edge Cases
Because the API takes many by-value vectors and a raw pointer to the client-status map, callers must ensure the map outlives the actor and that copying worker/storage metadata is acceptable. `deadlineTimeout` is part of the public contract; callers that pass too large a timeout can delay status responses, while too small a timeout increases partial results. The fault-tolerance helper assumes its input is valid full status JSON and will throw on parse errors.

## Test Signals
The implementation file includes a focused timeout unit test for `clusterGetStatus` and JSON tests for supporting builders. Compile/link tests that include this header validate type visibility for `StatusReply`, `ServerDBInfo`, `WorkerDetails`, `StorageServerMetaInfo`, `OpenDatabaseRequest`, and `ServerCoordinators`.
