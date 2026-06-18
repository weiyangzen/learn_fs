# sources/user-network-fs/samba/source3/rpc_client/cli_pipe.c research

## Purpose

`cli_pipe.c` is the central source3 DCE/RPC client transport and binding implementation. It creates `rpc_pipe_client` objects over named pipes, local ncalrpc sockets, and TCP; negotiates DCE/RPC bind and alter-context state; fragments outgoing requests; reassembles and verifies incoming fragments; and exposes a `dcerpc_binding_handle` implementation used by generated NDR client stubs. Higher-level files such as SAMR, SPOOLSS, WINREG, NETLOGON, and endpoint mapper clients depend on this layer to turn generated `dcerpc_*` calls into authenticated transport I/O.

## Important APIs, types, and functions

The file defines private state containers `struct rpc_client_association` and `struct rpc_client_connection`. An association owns the DCE/RPC binding, target address, negotiated bind-time features, and monotonically increasing call id. A connection owns the concrete `rpc_cli_transport`, transport session key, local address, maximum fragment sizes, bind completion state, header-signing state, and next auth/presentation context ids. These are moved into `struct rpc_pipe_client` by `rpc_pipe_wrap_create()`.

Core transport helpers are `rpc_read_send/recv()`, `rpc_write_send/recv()`, `cli_api_pipe_send/recv()`, `get_complete_frag_send/recv()`, and `rpc_api_pipe_send/recv()`. They provide tevent-based asynchronous read/write loops, optional transport-level transceive, full-fragment reads, packet unmarshalling, authentication verification, multi-fragment response assembly, and auth3 write-only handling.

Binding helpers include `rpc_pipe_bind_send()`, `rpc_pipe_bind_recv()`, synchronous `rpc_pipe_bind()`, `create_rpc_bind_req()`, `create_rpc_bind_auth3()`, `create_rpc_alter_context()`, `create_bind_or_alt_ctx_internal()`, `check_bind_response()`, `rpc_bind_next_send()`, and `rpc_bind_finish_send()`. These drive anonymous and authenticated bind handshakes, including GENSEC token exchange, alter-context legs, auth3 finalization, bind-time feature negotiation, and header-signing negotiation.

The `dcerpc_binding_handle` integration is implemented through `rpccli_bh_ops`. Key callbacks are `rpccli_bh_raw_call_send/recv()`, `rpccli_bh_disconnect_send/recv()`, `rpccli_bh_is_connected()`, `rpccli_bh_set_timeout()`, `rpccli_bh_transport_session_key()`, `rpccli_bh_auth_session_key()`, `rpccli_bh_auth_info()`, and `rpccli_bh_do_ndr_print()`. `rpccli_bh_create()` builds a handle whose advertised binding flags reflect the selected authentication type, auth level, header signing, and local address.

Public open/auth helpers include `rpccli_anon_bind_data()`, `rpccli_ncalrpc_bind_data()`, `rpc_pipe_open_ncalrpc()`, `rpc_pipe_open_local_np()`, `rpc_pipe_open_np_send/recv()`, `cli_rpc_pipe_open_noauth_transport()`, `cli_rpc_pipe_open_noauth()`, `cli_rpc_pipe_reopen_np_noauth()`, `cli_rpc_pipe_open_with_creds()`, `cli_rpc_pipe_client_prepare_alter()`, `cli_rpc_pipe_client_auth_schannel()`, `cli_rpc_pipe_open_bind_schannel()`, and `cli_rpc_pipe_open_schannel_with_creds()`.

## Control flow

Opening starts by selecting a transport endpoint. `cli_rpc_pipe_open()` resolves a remote name when needed, uses default endpoints when available, maps TCP interfaces through the endpoint mapper when no default port exists, creates an association, opens a connection through `rpc_pipe_open_tcp_port()` or `rpc_client_connection_np()`, and wraps the result into `rpc_pipe_client`. Named-pipe opens attach the client to the owning `cli_state->pipe_list`; the destructor removes it.

Binding begins in `rpc_pipe_bind_send()`. The function moves `pipe_auth_data` onto the client, assigns auth and presentation context ids when they are still sentinel values, creates a binding handle, captures the GENSEC username into `printer_username`, builds the initial bind or alter PDU, and sends it through `rpc_api_pipe_send()`. The response path validates packet type, call id, auth trailers, negotiated transfer syntax, fragment sizes, association group id, and bind result. If GENSEC returns more processing, it sends an alter-context PDU; if GENSEC returns a final token, it sends an auth3 PDU; otherwise the bind completes.

Request calls enter through generated NDR stubs via `rpccli_bh_raw_call_send()`. `rpc_api_pipe_req_send()` assigns a new call id, prepares a security verification trailer when packet-level auth is active, then calls `prepare_next_frag()` repeatedly. Non-final request fragments are written directly; the final fragment is sent through `rpc_api_pipe_send()` so the response is read. Replies are accumulated in `rpc_api_pipe_got_pdu()`, which validates each fragment, checks response auth with `dcerpc_check_auth()`, enforces stable endianness, caps total data with `MAX_RPC_DATA_SIZE`, and returns the assembled stub blob.

Endpoint mapping uses a nested anonymous bind to the endpoint mapper. `rpc_pipe_get_tcp_port()` opens and binds an EPM pipe, then calls `rpccli_epm_map_interface()` and `rpccli_epm_map_binding()` to resolve a TCP endpoint. `rpc_pipe_get_ncalrpc_name()` performs the analogous ncalrpc lookup unless the requested interface is EPM itself.

## State and persistence behavior

The file maintains in-memory state only. Association state persists across binds on a client: association group id, bind-time feature results, and call ids are retained. Connection state tracks max fragment sizes, bind completion, header signing, transport, local socket address, and the SMB application key when opened over named pipes. Authentication state is stored in `rpc_pipe_client->auth`; presentation context verification is recorded in `rpc_pipe_client->verified_pcontext`; security trailer verification records `verified_bitmask1` in the auth object.

Secrets include GENSEC credentials, transport session keys, and authentication session keys. Session keys are copied into caller memory and marked with `talloc_keep_secret()`. The code does not write persistent files. `cli_rpc_pipe_reopen_np_noauth()` deliberately resets association group id, negotiated feature bits, call id, auth, connection, presentation context id, and verification state before rebinding anonymously.

## Dependencies and integration points

The implementation depends on Samba's tevent, talloc, generated NDR DCE/RPC structures, `auth_generic`, GENSEC, credentials, endpoint mapper stubs, Netlogon credential helpers, SMB client state, `smbXcli` session APIs, socket helpers, local named-pipe helpers, npa streams, and transport implementations from `rpc_transport_np.c`, `rpc_transport_sock.c`, and `rpc_transport_tstream.c`. Generated NDR client files integrate through `dcerpc_binding_handle` callbacks, not by calling transport helpers directly.

It integrates with SMB named pipes through `rpc_transport_np_init_send/recv()` and captures the SMB application key for transport-session-key queries. It integrates with local server code through `local_np_connect()` and `rpc_transport_tstream_init()`. Schannel-specific helpers integrate with `netlogon_creds_cli_context`, and endpoint discovery integrates with the EPM generated client.

## Risks and edge cases

This file is security-critical. Packet validation must keep packet type, call id, flags, auth trailer length, auth type, auth level, auth context id, and header-signing negotiation aligned or callers could accept spoofed or malformed replies. The code frees `cli->conn` synchronously on several protocol/security failures; callers must treat the binding handle as disconnected afterward. Multi-fragment reply assembly relies on `MAX_RPC_DATA_SIZE` and the 15 MiB allocation-hint guard to resist oversized responses.

Authentication code assumes `cli->auth` exists in paths such as `prepare_next_frag()`; public open helpers always bind first, but future raw uses must preserve that contract. Bind-time feature negotiation consumes an extra presentation context id only when the negotiation result is acknowledged. `cli_rpc_pipe_client_prepare_alter()` can keep an old connection alive when security context multiplexing is unavailable; callers need to understand that association and connection lifetimes are intentionally decoupled.

Transport opening maps UNIX/socket errors into NTSTATUS and usually frees partial state. TCP endpoint mapping has nested RPC dependency on EPM availability. NCALRPC path construction must fit in `sockaddr_un.sun_path`. Named-pipe reconnect depends on a valid original `cli_state`.

## Test signals

Useful tests include anonymous bind to known interfaces, authenticated NTLM/KRB5/SPNEGO/SCHANNEL binds, alter-context with new auth and presentation contexts, SMB1 and SMB2 named-pipe opens, TCP endpoint-mapper resolution, ncalrpc endpoint resolution, connection drop and `cli_rpc_pipe_reopen_np_noauth()`, fragmented request/reply sizes near negotiated fragment limits, malformed packet type/call id/auth trailer cases, and header-signing negotiation with and without server support. Existing generated NDR callers should exercise `rpccli_bh_raw_call_send/recv()` paths; transport tests should assert that disconnect state is visible through `rpccli_is_connected()`.
