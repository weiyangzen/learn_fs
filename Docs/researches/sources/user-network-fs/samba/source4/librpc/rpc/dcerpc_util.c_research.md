# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_util.c

## Purpose

`dcerpc_util.c` provides utility operations around DCE/RPC interface lookup, endpoint mapper resolution, authentication policy selection, authentication fallback, session-key defaults, and secondary presentation contexts.

## Important APIs, Types, and Functions

Public functions include `dcerpc_iface_find_call()`, `dcerpc_epm_map_binding_send/recv()`, synchronous `dcerpc_epm_map_binding()`, `dcerpc_pipe_auth_send/recv()`, synchronous `dcerpc_pipe_auth()`, `dcecli_generic_session_key()`, and `dcerpc_secondary_context()`. Main state structs are `epm_map_binding_state` and `pipe_auth_state`.

## Control Flow

Endpoint mapping first sets the abstract syntax, scans IDL default endpoints for a matching transport, and otherwise connects anonymously to epmapper, builds an EPM tower, calls `epm_Map`, validates one returned tower, extracts floor 3 RHS endpoint data, and writes it into the binding. Authentication chooses no-auth for anonymous credentials, special ncalrpc-as-system auth for configured local bindings, schannel setup when requested and missing netlogon creds, implicit no-auth over unsigned named pipes, or authenticated bind with SPNEGO/KRB5/schannel/NTLM. Auto auth starts with SPNEGO and can retry with NTLMSSP or a better password on a secondary connection.

## State and Persistence Behavior

The code mutates connection flags from binding flags and can replace the caller's pipe during authentication fallback. It stores endpoint and abstract-syntax data in the binding and creates secondary context IDs via `dcerpc_alter_context()`. It does not write persistent data.

## Dependencies and Integration Points

Dependencies include epmapper generated stubs, NDR tower helpers, credentials, GENSEC settings, schannel helpers, secondary connection helpers, bind/auth functions in core DCE/RPC, and loadparm. It is central glue used by connection code, Python bindings, schannel, and callers that need endpoint lookup.

## Risks and Test Signals

Risks include incorrect default endpoint selection, tower floor assumptions, auth fallback ownership changes, implicit sign defaulting, anonymous/no-auth over SMB named pipes relying on SMB-layer auth, and handling of wrong-password retries. Tests should cover default endpoints, EPM lookup, SPNEGO success, SPNEGO-to-NTLM fallback, Kerberos wrong-password retry, schannel, ncalrpc-as-system, and `alter_context` secondary context creation.
