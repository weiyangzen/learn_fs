# sources/user-network-fs/impacket/impacket/dcerpc/v5/rpch.py

## Purpose

`rpch.py` implements Impacket's RPC over HTTP v2 client support, including RTS PDU structures and a transport-like `RPCProxyClient` built on `HTTPClientSecurityProvider`. It establishes paired `RPC_IN_DATA` and `RPC_OUT_DATA` HTTP channels, performs RPC proxy authentication, creates the virtual connection tunnel, reads RPC and RTS packets from the outbound channel, sends RPC data on the inbound channel, and maintains flow-control acknowledgments.

## Important APIs, Types, And Functions

The module exports RPC-over-HTTP version constants, proxy error strings, forward destination constants, RTS flags, RTS command constants, `RPCProxyClientException`, RTS command structures, helper packet builders, and `RPCProxyClient`.

RTS structures include `RTSCookie`, `EncodedClientAddress`, `Ack`, command wrappers such as `ReceiveWindowSize`, `FlowControlAck`, `ConnectionTimeout`, `Cookie`, `ChannelLifetime`, `ClientKeepalive`, `Version`, `Empty`, `Padding`, `NegativeANCE`, `ANCE`, `ClientAddress`, `AssociationGroupId`, `Destination`, and `PingTrafficSentNotify`, plus `RTSHeader`. Higher-level RTS PDUs include `CONN_A1_RTS_PDU`, `CONN_B1_RTS_PDU`, `CONN_A3_RTS_PDU`, `CONN_C2_RTS_PDU`, and `FlowControlAckWithDestination_RTS_PDU`.

Helpers `hCONN_A1`, `hCONN_B1`, `hFlowControlAckWithDestination`, and `hPing` return serialized RTS packets. `RPCProxyClient` exposes `connect`, `disconnect`, `send`, `recv`, channel creation/closing methods, `rpc_out_read_pkt`, `rpc_out_recv1`, `flow_control`, and `handle_out_of_sequence_rts`.

## Control Flow

`RPCProxyClient.connect()` creates the inbound and outbound HTTP channels, then calls `create_tunnel()`. Channel creation prepares RPC proxy headers, obtains authentication headers from `HTTPClientSecurityProvider`, derives or validates the remote RPC server name, adds `?RemoteName:Port` to the RPC proxy URL when needed, sends the HTTP method request, and waits for an HTTP 100 Continue response.

Tunnel creation sends CONN/A1 on the out channel and CONN/B1 on the in channel, reads the outbound HTTP 200 response, detects chunked transfer encoding, preserves any body bytes already received, then parses CONN/A3 and CONN/C2 RTS PDUs to capture server timeout and receive-window values.

Outbound reads use `rpc_out_read_pkt()`: read the common RPC header, read exactly `frag_len`, apply flow control to non-RTS packets, and either handle out-of-sequence RTS packets or return the packet. `rpc_out_recv1()` abstracts normal and chunked HTTP body reads while preserving over-read bytes. `flow_control()` sends a `FlowControlAckWithDestination` packet when the advertised receive window drops below half. `handle_out_of_sequence_rts()` replies to ping RTS packets and rejects channel recycle requests.

## State And Persistence Behavior

There is no disk persistence. Runtime state includes HTTP channel objects, generated cookies, association group ID, virtual connection cookie, server timeout/window values, advertised and remaining receive windows, bytes received, chunked transfer state, read buffer leftovers, and an `rts_ping_received` flag. `disconnect()` closes both channels and resets state via `init_state()`.

The class mutates the transport string binding when it learns the RPC proxy NetBIOS name from NTLMSSP. It also caches the remote name for later channel creation.

## Dependencies And Integration Points

The module depends on `re`, `binascii`, `struct.unpack`, Impacket `uuid`, `ntlm`, system and NT error tables, `LOG`, `EMPTY_UUID`, `HTTPClientSecurityProvider`, `AUTH_BASIC`, `Structure`, and constants/classes from `rpcrt.py`. It is an integration layer between Impacket's HTTP authentication stack and `rpcrt.DCERPC_v5`, which can use this object as an RPC transport provider. Exchange NSPI and OXABREF workflows are important consumers.

## Risks And Edge Cases

HTTP parsing is intentionally narrow and stream-oriented. The code reads until CRLFCRLF for response headers, checks fixed byte offsets in status lines, and handles localized errors only in the first line. Chunked decoding tracks one chunk at a time and assumes well-formed chunk-size lines and trailing CRLF; malformed proxies can desynchronize the read buffer. HTTP 503 RPC errors are detected by a fixed prefix.

RPC proxy behavior differs across Exchange and RD Gateway deployments, and the code contains assumptions about valid ports, remote names, and NTLM-derived host names. Basic auth requires an explicit remote name. Long-lived idle tunnels are not fully supported: a ping RTS packet is treated as a sign of likely server-side trouble, though the client sends pings back. Channel recycle requests are explicitly unsupported.

## Test Signals

Unit tests should serialize all RTS helper packets and validate flags, command counts, cookies, and window values. Stream tests should cover non-chunked reads, chunked reads with split chunk headers, over-read buffering, HTTP error injection, and RTS packet interleaving. Authentication/channel tests can mock `HTTPClientSecurityProvider` to verify Basic-auth remote-name failure, NTLM-derived remote names, RPC proxy query construction, and 100 Continue handling. Integration tests need an RPC proxy or Exchange endpoint and should verify bind and request flow through `rpcrt.DCERPC_v5`.
