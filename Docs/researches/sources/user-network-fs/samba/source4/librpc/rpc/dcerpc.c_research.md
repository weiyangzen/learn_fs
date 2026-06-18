# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.c

## Purpose

`dcerpc.c` implements the core source4 DCE/RPC client runtime: pipe initialization, binding handles, NCACN bind/alter/auth3 packet handling, request queueing, fragmentation, signing/sealing hooks, response reassembly, timeout/error handling, NDR validation/debugging, and tstream transport IO.

## Important APIs, Types, And Functions

Private `struct rpc_request` tracks queued/pending/done state, pipe pointer, NTSTATUS, call id, payload, PDU flags, fault code, optional special receive handler for bind/alter, object UUID, opnum, request blob, timeout flags, verification-trailer state, and async callback.

`dcerpc_init()` initializes GENSEC. `dcerpc_pipe_init()` allocates a `dcerpc_pipe` and `dcecli_connection`, sets default fragment sizes and timeout, and enables debug printing at high debug levels. `dcerpc_pipe_binding_handle()` creates a generic `dcerpc_binding_handle` backed by `dcerpc_bh_ops`.

Binding-handle operations provide binding lookup, connected state, timeout setting, transport encryption/session key, auth info/session key, raw call send/recv, disconnect, endian/ref/NDR64 flags, debug printing, NDR push/pull failure logging, and optional NDR validation.

Protocol functions include `dcerpc_bind_send/recv`, `dcerpc_auth3()`, `dcerpc_alter_context_send/recv`, and synchronous `dcerpc_alter_context()`. IO functions include `dcerpc_request_send/recv`, `dcerpc_request_prepare_vt()`, `dcerpc_ship_next_request()`, `dcerpc_recv_data()`, `dcerpc_request_recv_data()`, `dcerpc_send_read()`, and `dcerpc_send_request()`.

## Control Flow

Normal RPC calls enter through the binding-handle raw call operation, which creates an `rpc_request` with a new call id and enqueues it. `dcerpc_schedule_io_trigger()` schedules a tevent immediate. `dcerpc_ship_next_request()` moves the first queued request to pending, builds one or more request PDUs respecting negotiated fragment sizes and auth trailer/signature overhead, writes them via the tstream write queue, and starts reads. If authenticated GENSEC does not support async replies, later requests wait for pending requests to drain.

Incoming transport blobs are parsed by `dcerpc_recv_data()` into NCACN packets and dispatched by `dcerpc_request_recv_data()`. Responses are matched by call id, authenticated before request lookup state is trusted, appended across fragments, size-checked against `max_total_response_size`, and completed on the last fragment. Fault packets map DCE/RPC fault codes to NTSTATUS, with severe protocol/security faults killing the connection.

Bind and alter-context requests are special pending `rpc_request` objects with custom receive handlers. `dcerpc_bind_send()` sends a bind with the requested abstract/transfer syntax and a second bind-time-features context. The bind reply handler validates packet type/flags, maps NAK/ACK reasons, negotiates fragment sizes, concurrent multiplexing, header signing, auth trailers, association group id, and binding abstract syntax. Alter-context follows a similar path with one context and fault handling.

## State And Persistence Behavior

All state is in-memory and talloc-owned by the pipe/connection/request. Persistent effects are remote: bind association state on the server and RPC operations sent through this client. `dcecli_connection` tracks call ids, negotiated fragment sizes, flags, security state, pending and queued requests, transport stream/queue/read state, server name, and negotiated bind-time features. Connection death marks the connection dead, shuts down the stream, and completes all queued/pending requests with the same error.

## Dependencies And Integration Points

The file integrates `tevent`, talloc, generated DCERPC NDR types, GENSEC, `dcerpc_pkt_auth`, DCE/RPC utility code, tsocket/tstream, SMB named-pipe tstream helpers, and public binding-handle APIs. Higher-level generated RPC clients use the binding handle created here.

## Risks

This is concurrency- and security-sensitive code. Request queueing must preserve call-id matching and avoid reentrant callbacks; the code defers callbacks for that reason. Fragment sizing must account for object UUIDs, auth trailers, signature sizes, and alignment. Auth verification trailers (`BITMASK1`, `PCONTEXT`, `HEADER2`) are appended for packet-level auth and must be synchronized with server verification state. Connection teardown during callbacks can interact with talloc destructors. Response size limits guard against unbounded reassembly but can reject legitimate large responses if configured too low.

## Test Signals

Key tests include unauthenticated bind and calls, authenticated bind with multi-step GENSEC and auth3, alter-context to another transfer syntax, fragmented request/response round trips, concurrent multiplexing behavior, timeout handling, unmatched call-id responses, fault mapping, NDR validation flags, big-endian/NDR64 modes, packet logging on pull failure, and transport close/error propagation.
