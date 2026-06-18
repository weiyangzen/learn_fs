# sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.c

Purpose: Samba4 DCE/RPC server transport glue. It initializes RPC server modules, manages association groups, accepts stream connections, registers endpoint listeners, exposes messaging/server id helpers, prepares GENSEC auth, and terminates transports.

Important APIs and control flow: association-group helpers allocate random IDs in an IDR, validate transport compatibility, reference groups to connections, and remove them in destructors. `dcerpc_server_init()` runs static and shared `dcerpc_server` module initializers once. `dcesrv_sock_accept()` creates anonymous session info when needed, calls `dcesrv_endpoint_connect()`, installs stream transport callbacks, builds a tstream from named pipe or socket fd, handles NCALRPC peer credentials and system-token path mapping, then starts `dcesrv_connection_loop_start()`. Endpoint adders register Unix stream, NCALRPC, named pipe, and TCP sockets. `dcesrv_add_ep()` dispatches by binding transport. Auth helpers log successful authorization and start server-side GENSEC.

State and persistence: no durable storage, but it owns process runtime state: listener sockets, connection transport private data, send queues, talloc references, and association group counts/IDs.

Dependencies and integration: connects core `librpc/rpc/dcesrv_core.h` to Samba stream services, process models, socket/tstream, tsocket addresses, gensec, credentials, messaging, and module loading.

Risks and test signals: transport setup is high blast radius. Test binding to configured interfaces, wildcard TCP, NCALRPC default endpoint, named pipe endpoint validation, peer credential handling, association group reuse/rejection across transports, auth event logging, and cleanup of broken connections.
