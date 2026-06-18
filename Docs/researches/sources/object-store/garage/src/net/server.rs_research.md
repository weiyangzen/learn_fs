# sources/object-store/garage/src/net/server.rs

Purpose: server-side NetApp connection handling. It authenticates inbound TCP sockets with `kuska_handshake`, wraps them in encrypted `BoxStream`s, sends the Garage version tag, and then runs receive/send loops for request/response streams.

Important APIs and types: `ServerConn` stores the remote socket address, authenticated peer `NodeID`, parent `NetApp`, an `ArcSwapOption` response channel, and a `Mutex<HashMap<RequestID, JoinHandle<()>>>` of running request handlers. `ServerConn::run` is the lifecycle entry point. `recv_handler_aux` resolves a request path into a registered endpoint and invokes the endpoint handler. The `RecvLoop` implementation spawns one task per request and `cancel_handler` aborts outstanding tasks.

Control flow: after handshake and version-tag write, `run` registers the connection as server-side with `NetApp`, starts `recv_loop` under `select!` with `await_exit`, starts `send_loop`, and tears down sender state when receive finishes. Each decoded `ReqEnc` carries priority, path, body, and optional telemetry context; responses are converted with `RespEnc::encode` and sent through `SendItem::Stream`.

State and persistence: no disk persistence. Runtime state is the response channel and in-flight handler map. Cancellation removes the join handle and sends `SendItem::Cancel` so the send loop can suppress the response.

Dependencies and integration: integrates with `netapp`, `endpoint` handlers, stream/message encoding, `tokio` tasks/channels, `arc-swap`, `futures`, and optional OpenTelemetry trace propagation.

Risks and test signals: per-request task spawning makes cancellation correctness important. A dropped response channel silently discards late work. Handler map locking must remain short. Telemetry is feature-gated. Network behavior is indirectly covered by ignored flaky peering tests in `net/test.rs`.
