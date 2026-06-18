# sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.h

Purpose: internal DRSUAPI server header shared by the main endpoint, add-entry implementation, get-changes implementation, update-ref code, and utility helpers.

Important APIs/types: defines `enum drsuapi_handle` with `DRSUAPI_BIND_HANDLE`; defines `drsuapi_bind_state` containing remote/local bind info, remote bind GUID, user samdb context, and optional system samdb context. Declares RPC method implementations for update refs, get NC changes, add entry, write account SPN, object identifier formatting, extended-DN search, security level/access checks, and secret attribute redaction.

State and persistence: the bind state is the per-handle runtime context for DRS calls. Persistence is delegated to implementations declared here.

Dependencies and integration: includes generated DRSUAPI IDL types, SAMDB, security tokens, and DCE/RPC call state. It is the contract between `dcesrv_drsuapi.c`, `addentry.c`, `drsutil.c`, and other DRS server modules.

Risks and test signals: handle type and bind state changes affect every DRS call. Compile coverage should include all DRS modules; behavioral tests should validate bind handle pull/create/free paths and system-context availability for RODC cases.
