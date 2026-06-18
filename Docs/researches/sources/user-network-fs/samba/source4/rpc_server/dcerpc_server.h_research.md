# sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.h

Purpose: public Samba4 RPC server header that exposes endpoint registration and connection-context helpers.

Important APIs/types: forward-declares `struct model_ops`; declares `dcesrv_add_ep()` for adding a configured endpoint to an event loop and process model; declares `_PUBLIC_ dcesrv_imessaging_context()` and `_PUBLIC_ dcesrv_server_id()` for retrieving the stream connection messaging context and server id from a `dcesrv_connection`.

State and persistence: no state; this is an interface contract.

Dependencies and integration: includes `librpc/rpc/dcesrv_core.h`, so users get core DCE/RPC server types. Implemented by `dcerpc_server.c`; used by forwarding, DNS server, DRSUAPI, common helpers, and other RPC server modules.

Risks and test signals: ABI/API changes affect modules. Compile coverage should include modules that register endpoints and those that retrieve messaging/server-id data for IRPC forwarding.
