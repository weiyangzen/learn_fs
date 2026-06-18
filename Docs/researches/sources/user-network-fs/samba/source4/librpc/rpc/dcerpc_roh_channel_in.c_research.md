# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_in.c

## Purpose

`dcerpc_roh_channel_in.c` implements the inbound-channel pieces of the RPC-over-HTTP opening handshake: sending the long-lived `RPC_IN_DATA` HTTP request and sending RTS `CONN/B1` on that channel.

## Important APIs, Types, And Functions

`struct roh_request_state` stores HTTP request/response pointers for `RPC_IN_DATA`. `roh_send_RPC_DATA_IN_send/recv()` builds and sends the authenticated HTTP request. `struct roh_send_pdu_state` stores the serialized RTS PDU buffer, iovec, bytes-written result, and errno. `roh_send_CONN_B1_send/recv()` constructs and writes the RTS CONN/B1 packet.

## Control Flow

`roh_send_RPC_DATA_IN_send()` constructs URI `/rpc/rpcproxy.dll?<rpc_server>:<rpc_server_port>`, sets request type `HTTP_REQ_RPC_IN_DATA`, HTTP/1.0 version markers, zero body, large `Content-Length` of `1073741824`, and headers such as `Accept: application/rpc`, `User-Agent: MSRPC`, `Host`, keep-alive, no-cache, and pragma. It sends the request through `http_send_auth_request_send()` on `roh->default_channel_in->http_conn` using the selected HTTP auth method.

`roh_send_CONN_B1_send()` builds a DCERPC RTS packet with six commands: version, virtual connection cookie, in-channel cookie, channel lifetime/receive-window value, client keepalive, and association group id. It serializes `ncacn_packet` with little-endian DREP, type `DCERPC_PKT_RTS`, first/last flags, fixed frag length 104, and writes it via the HTTP connection tstream send queue for the default in channel.

## State And Persistence Behavior

The functions mutate only transient request state and write to the existing HTTP in-channel. `CONN/B1` reads cookies from `roh_connection` and channel state; it does not update connection state itself. The broader state transition is handled in `dcerpc_roh.c` after recv functions return success.

## Dependencies And Integration Points

The file depends on tevent, talloc, tsocket, TLS headers, credentials, generated DCERPC NDR types, DCE/RPC ROH structs, and HTTP helpers. It is called by `dcerpc_roh.c` during ROH open sequencing.

## Risks

The large fixed content length and HTTP/1.0/keep-alive behavior are protocol compatibility details; changing them can break RPC proxies. `CONN/B1` uses literal command type numbers rather than the named macros in the header, making accidental mismatch easier. The write completion treats `bytes_written <= 0 && errno != 0` as failure; short positive writes rely on tstream semantics to mean completion.

## Test Signals

Unit tests should inspect the generated HTTP request URI/headers/body, auth method propagation, serialized RTS command count and cookies, fixed fragment length, send queue selection, and error propagation from HTTP auth send and tstream write.
