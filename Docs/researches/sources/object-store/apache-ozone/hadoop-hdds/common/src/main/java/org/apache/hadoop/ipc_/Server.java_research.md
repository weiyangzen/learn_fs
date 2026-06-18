# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Server.java

## Purpose
`Server` is the abstract Hadoop IPC server implementation vendored under Ozone's `org.apache.hadoop.ipc_` namespace. It owns the listening socket, nonblocking accept/read/write loops, per-connection state, SASL negotiation, service authorization, request deserialization, call queue integration, handler execution, response serialization, metrics, slow-RPC accounting, and idle connection cleanup. Subclasses implement the abstract `call(RPC.RpcKind, String, Writable, long)` hook to dispatch decoded RPC payloads to a protocol implementation.

## Important APIs, types, and functions
- Static RPC engine registry: `registerProtocolEngine`, `getRpcRequestWrapper`, and `getRpcInvoker` map an `RPC.RpcKind` to a request wrapper class and invoker. `getProtocolClass` caches protocol classes by name.
- Runtime context APIs: `getCurCall`, `getCallId`, `getRemoteIp`, `getClientId`, `getRemoteAddress`, and `getRemoteUser` expose the current handler-thread RPC context via `ThreadLocal`.
- `Call` implements `Schedulable` and `PrivilegedExceptionAction<Void>`. It carries call id, retry count, client id, caller context, processing details, scheduler priority, optional client state id, and response lifecycle counters.
- `RpcCall` extends `Call` with `Connection`, deserialized `Writable` request, response bytes, and response status/error fields. Its `run` method invokes the abstract server `call`, records processing timing, and schedules response send.
- `Listener` accepts sockets, binds to fixed or ranged ports, fans accepted sockets to `Reader` threads, and starts/stops idle scanning.
- `Listener.Reader` registers accepted channels with a read selector and calls `Connection.readAndProcess`.
- `Responder` owns the write selector and response queues. It writes immediately when possible, registers partial responses for `OP_WRITE`, purges responses that have been pending too long, and SASL-wraps queued responses when negotiated QoP requires it.
- `Connection` holds channel/socket state, connection header and context state, SASL state, auth method, user/proxy user, protocol name, packet buffers, response queue, outstanding RPC count, and remote address details.
- `ConnectionManager` tracks active connections, dropped connections, open connections per user, max connection enforcement, idle close policy, and timer-driven idle scans.
- Lifecycle and inspection APIs include `start`, `stop`, `join`, `getListenerAddress`, `getPort`, `getNumOpenConnections`, `getNumOpenConnectionsPerUser`, `getNumDroppedConnections`, `getCallQueueLen`, and `getServerName`.

## Control flow
Construction configures queue classes and scheduler classes from `ipc.<port>.*`, builds supported auth methods, binds `Listener`, creates metrics, initializes SASL helpers when security or tokens are enabled, and creates the `Responder`. `start` starts responder, listener, and handler threads.

Connection setup starts with `Listener.doAccept`, which configures nonblocking TCP, registers a `Connection` with `ConnectionManager`, and assigns it to a reader. `Connection.readAndProcess` first reads the Hadoop RPC magic header, validates IPC version and auth protocol, detects accidental HTTP GETs, then reads framed RPC packets. Negative call ids route to out-of-band handling: SASL negotiation, connection context, and ping. Nonnegative call ids require an authorized connection context, then flow through `processRpcRequest`.

`processRpcRequest` rejects unsupported Writable RPC and rejects unregistered RPC kinds before deserializing payloads. It creates a `RpcCall`, attaches caller context, assigns scheduler priority, optionally coordinates with `AlignmentContext`, and enqueues the call through `CallQueueManager`. Handler threads take calls, optionally requeue coordinated calls until state catches up, set `CurCall` and `CallerContext`, execute under the remote user's `doAs` when available, and update queue, lock, processing, response, detailed method, scheduler response time, and slow-RPC metrics.

Responses are assembled in `setupResponse`: protobuf-style responses are serialized into a preallocated byte array with a length prefix, while non-protobuf `Writable` responses use a reusable `ResponseBuffer`. Fatal responses mark the connection for close. `Responder.doRespond` appends the response to the per-connection queue, tries immediate nonblocking write, and uses the write selector for partial writes.

## State and persistence behavior
State is in-memory and thread-scoped: active connections, per-user connection counters, queues, response buffers, metrics objects, SASL contexts, `ThreadLocal` current calls, and scheduler state. The class does not persist user data. It does produce externally visible protocol state over sockets and metrics through Hadoop metrics. Idle scan scheduling uses a daemon `Timer`; shutdown cancels scans, closes sockets/channels, interrupts threads, and unregisters metrics.

## Dependencies and integration points
This class integrates with Hadoop configuration keys, `CallQueueManager`, `RpcScheduler`, `FairCallQueue`, `DecayRpcScheduler`, `RpcWritable`, protobuf RPC headers, `SaslRpcServer`, `SaslPropertiesResolver`, `UserGroupInformation`, delegation-token `SecretManager`, `ProxyUsers`, `ServiceAuthorizationManager`, `AlignmentContext`, and metrics classes `RpcMetrics`/`RpcDetailedMetrics`. It is extended by `RPC.Server` and depends on registered protocol engines such as protobuf RPC.

## Risks and edge cases
- Security-sensitive paths include SASL negotiation, token auth, proxy-user checks, protocol authorization, and the HADOOP-19864 pre-deserialization registered-protocol check.
- Multiple selector and handler threads coordinate through shared queues, atomics, and synchronized blocks. Races are intentionally tolerated in some areas, but response ordering and SASL wrapping rely on per-connection response queue synchronization.
- `Connection.readAndProcess` allocates a `ByteBuffer` of packet length after checking `maxDataLength`; incorrect limits would become memory pressure or denial-of-service risks.
- Fatal responses set `shouldClose`; callers must preserve that invariant so invalid protocol state cannot continue on a connection.
- Large responses are only logged, not rejected, so memory and socket backpressure still depend on caller behavior and `maxRespSize` only bounds buffer reuse.
- `ConnectionManager.getUserToConnectionsMap` exposes the concurrent map directly to JSON serialization while updates use a separate lock, so metric snapshots are eventually consistent.

## Test signals
Useful tests should cover version mismatch responses, HTTP-on-IPC response, unsupported auth protocol, SIMPLE disabled, SASL token/Kerberos negotiation, proxy user authorization failures, unregistered RPC kind rejection before deserialization, queue overflow/backoff, coordinated-call requeue, response serialization failure fallback, idle connection cleanup, per-user connection counters, metrics increments, and shutdown cleanup. Existing Hadoop IPC tests such as `TestServer`, `TestMultipleProtocolServer`, SASL/security tests, and queue/scheduler tests are the most relevant signal class.
