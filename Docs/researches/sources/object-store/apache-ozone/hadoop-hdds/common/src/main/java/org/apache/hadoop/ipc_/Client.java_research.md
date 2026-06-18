# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Client.java

## Purpose
Implements the Hadoop-style IPC client used by Ozone's shaded IPC stack, including connection pooling, request multiplexing, SASL negotiation, pings, retries, response demultiplexing, and call lifecycle management.

## Important APIs, Types, And Functions
Important APIs include ping/timeout config helpers, `call`, `stop`, `close`, `nextCallId`, and `ConnectionId.getConnectionId`. Nested types are `Call`, `Connection`, `Connection.PingInputStream`, `Connection.RpcRequestSender`, `ConnectionId`, and `IpcStreams`.

## Control Flow
`call()` creates a `Call`, attaches optional `AlignmentContext`, obtains or creates a pooled `Connection`, serializes and queues the request, then waits for completion. `Connection.setupIOstreams()` establishes sockets, writes the IPC header, performs SASL if needed, writes connection context, starts the receiver thread and request-sender thread. The sender serializes request buffers to the socket; the receiver reads framed responses, checks client ID, parses headers, updates alignment state on success, completes matching calls, or closes the connection on fatal errors.

## State And Persistence
Client state includes a concurrent connection map, running flag, ref count, socket factory, value class, configuration, client UUID bytes, and per-thread call ID/retry count. Each connection owns socket/streams, active call table, retry config, SASL state, activity timestamps, close reason, and request queue. No durable persistence is owned.

## Dependencies And Integration Points
Integrates Hadoop configuration/security/UGI, NetUtils, SASL RPC client, RPC header protobufs, `RpcWritable`, `ResponseBuffer`, `RetryPolicies`, `AlignmentContext`, `RemoteException`, and server IPC framing constants. `RetryInvocationHandler` injects call ID and retry count for RPC retries.

## Risks
This is a high-concurrency class: call table cleanup, connection replacement, sender/receiver shutdown, and interrupt handling must stay consistent. Client ID mismatch closes calls. SASL fallback is security-sensitive. `ConnectionId.equals()` includes many config fields but not all constructor fields such as max socket timeout retries. Large responses are bounded only by configured max length.

## Test Signals
Coverage should include connection reuse, stop behavior, call interruption, response demux, fatal vs error responses, SASL success/fallback/failure, ping timeouts, address refresh, max response length, and alignment-context state. OM HA and secure-cluster integration tests exercise important RPC paths.
